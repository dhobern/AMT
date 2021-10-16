import math as math
from idac.objectOfInterrest import ObjectOfInterrest
import numpy as np
from scipy.optimize import linear_sum_assignment
import time
from abc import ABC, abstractmethod

def getdirection(a, b):
    ax, ay = a["xcenter"], a["ycenter"]
    bx, by = b["xcenter"], b["ycenter"]
    x = bx - ax
    y = by - ay
    if (x ** 2) + (y ** 2) > 100:
        return math.atan2(y,x)/math.pi*180
    else:
        return ""

class Scale(ABC):

    def __init__(self):
        self.weight = 1

    @abstractmethod
    def measurecost(self, a, b):
        pass

    @abstractmethod
    def getcode(self):
        pass

    def setweight(self, conf):
        if "weight" in conf:
            self.weight = conf["weight"]

    def getweight(self):
        return self.weight

class AMTSizeScale(Scale):

    def measurecost(self, a, b):
        asize = a["size"]
        bsize = b["size"]
        if asize > bsize:
            temp = asize
            asize = bsize 
            bsize = temp
        ratio = bsize / asize
        if ratio > 4:
            return self.weight
        return self.weight * (ratio - 1) / 3

    def getcode(self):
        return "S"

class AMTDistanceScale(Scale):

    def measurecost(self, a, b):
        ax, ay = a["xcenter"], a["ycenter"]
        bx, by = b["xcenter"], b["ycenter"]
        distance = math.sqrt((bx - ax) ** 2 + (by - ay) ** 2)

        if distance < 25:
            penaltydistance = 0
        elif bx > a["x"] and bx < a["x"] + a["w"] and by > a["y"] and by < a["y"] + a["h"]:
            penaltydistance = 0.01
        elif distance < 100:
            penaltydistance = 0.01
        elif distance < 250:
            penaltydistance = 0.02
        else: 
            #Distance as fraction of possible distance - in range 0.0-1.0
            penaltydistance = distance / 4405

        return self.weight * penaltydistance

    def getcode(self):
        return "D"

class AMTColorScale(Scale):

    def __init__(self):
        self.colors = [ "R", "G", "B", "C", "M", "Y", "W", "K" ]

    def measurecost(self, a, b):
        distance = 0
        acolors = a["colors"]
        bcolors = b["colors"]
        for c in self.colors:
            if (c in acolors) != (c in bcolors):
                distance += 1
        return self.weight * distance / len(self.colors)
        
    def getcode(self):
        return "C"

class AMTAgeScale(Scale):

    def measurecost(self, a, b):

        if a["age"] > 5:
            return self.weight
        else:
            return self.weight * a["age"] / 5

    def getcode(self):
        return "A"

class AMTDirectionScale(Scale):

    def measurecost(self, a, b):
        if a["direction"] == "":
            return 0
        
        direction = getdirection(a, b)

        if direction == "":
            return 0

        difference = a["direction"] - direction
        if difference < -180:
            difference += 360
        elif difference > 180:
            difference -= 360

        return self.weight * abs(difference) / 180

    def getcode(self):
        return "B"

class AMTScaleFactory:

    def create(self, conf):
        classname = conf["class"]
        if classname == "AMTSizeScale":
            scale = AMTSizeScale()
        elif classname == "AMTDistanceScale":
            scale = AMTDistanceScale()
        elif classname == "AMTDirectionScale":
            scale = AMTDirectionScale()
        elif classname == "AMTAgeScale":
            scale = AMTAgeScale()
        elif classname == "AMTColorScale":
            scale = AMTColorScale()
        else:
            print("No Scale class " + classname + " defined")
            return None
        scale.setweight(conf)
        return scale

class AMTTracker:

    def __init__(self, conf):
        self.savedois = []
        self.conf = conf["tracker"]
        self.scales = []
        self.totalweight = 0
        factory = AMTScaleFactory()
        for s in self.conf["scales"]:
            if s["class"] is not None:
                scale = factory.create(s)
                self.scales.append(scale)
                self.totalweight += scale.getweight()
        self.maxage = self.conf["maxage"]
        self.cost_threshold = self.conf["cost_threshold"]

    def blobsmatch(self, blob1, blob2):
        # For this purpose, a match is considered good if the centroids of the 
        # blobs are in the innnermost 10% of the other blob and if the sizes are
        # within 20%.

        x1 = blob1["x"]
        y1 = blob1["y"]
        w1 = blob1["w"]
        h1 = blob1["h"]
        x2 = blob2["x"]
        y2 = blob2["y"]
        w2 = blob2["w"]
        h2 = blob2["h"]

        cx1 = blob1["xcenter"]
        cy1 = blob1["ycenter"]
        cx2 = blob2["xcenter"]
        cy2 = blob2["ycenter"]

        size1 = w1 * h1
        size2 = w2 * h2

        if (size2 > size1 and size2 > size1 * 1.2) or (size1 > size2 and size1 > size2 * 1.2):
            return False

        if cx1 < x2 + (w2 * 0.4) or cx1 > x2 + (w2 * 0.6) or cy1 < y2 + (h2 * 0.4) or cy1 > y2 + (h2 * 0.56):
            return False

        if cx2 < x1 + (w1 * 0.4) or cx2 > x1 + (w1 * 0.6) or cy2 < y1 + (h1 * 0.4) or cy2 > y1 + (h1 * 0.6):
            return False

        return True    

    def compare(self, a, b):
        comparison = 0
        cstring = ""
        for s in self.scales:
            distance = s.measurecost(a, b)
            comparison += distance ** 2
            sstring = s.getcode() + ":" + str(distance)
            if len(sstring) > 7:
                sstring = sstring[0:7]
            if len(cstring) > 0:
                cstring += ";" + sstring
            else:
                cstring = sstring
        return math.sqrt(comparison / self.totalweight), cstring

    def managetracks(self, tracks, blobs):
        newtracks = []

        t = 0
        while t < len(tracks):
            track = tracks[t]
            b = 0
            found = False
            while not found and b < len(blobs):
                blob = blobs[b]
                if self.blobsmatch(track, blob):
                    found = True
                    blob["trackid"] = track["trackid"]
                    blob["cost"] = 0
                    blob["weights"] = "HighOverlap"
                    newtracks.append(blobs[b])
                    blobs.pop(b)
                    tracks.pop(t)
                else:
                    b += 1
            if not found:
                # Leave this track for weighted comparisons
                t += 1
            else:
                # tracks is now one shorter so try the same index
                pass

        if len(blobs) > 0 and len(tracks) > 0:
            max_size = len(tracks) if len(tracks) > len(blobs) else len(blobs)
            costs = np.full((max_size, max_size), 8.1)

            cstrings = []
            for t in range(len(tracks)):
                cstringrow = []
                cstrings.append(cstringrow)
                for b in range(len(blobs)):
                    costs[t][b], cstring = self.compare(tracks[t], blobs[b])
                    cstringrow.append(cstring)

            if False: # Show cost matrix
                colnames = "Blobs"
                sep = ": "
                for b in blobs:
                    colnames += sep + str(b["id"])
                    sep = ", "
                print(colnames)
                for t in range(len(tracks)):
                    print(str(tracks[t]["trackid"]) + ": " + str(costs[t]))
                #print(str(len(tracks)) + " / " + str(len(blobs)) + " / " + str(costs))
            
            track_ind, blob_ind = linear_sum_assignment(costs)

            for i in range(len(track_ind)):
                if costs[track_ind[i]][blob_ind[i]] < self.cost_threshold:
                    track = tracks[track_ind[i]]
                    blob = blobs[blob_ind[i]]
                    blob["trackid"] = track["trackid"]
                    blob["direction"] = getdirection(track, blob)
                    blob["age"] = 0
                    blob["delay"] = track["age"]
                    blob["cost"] = costs[track_ind[i]][blob_ind[i]]
                    blob["weights"] = cstrings[track_ind[i]][blob_ind[i]]
                    newtracks.append(blob)
                    tracks[track_ind[i]] = None
                    blobs[blob_ind[i]] = None

        # At this point, newtracks contains all the blobs that match, tracks
        # contains other blobs from the last image, and blobs contains the 
        # currently unmatched blobs. 

        t = 0
        while t < len(tracks):
            track = tracks[t]
            if track is not None and track["age"] <  5:
                track["age"] = track["age"] + 1
                newtracks.append(track)
                tracks.pop(t)
            else:
                t += 1

        # All remaining blobs are new tracks
        for blob in blobs:
            if blob is not None:
                blob["trackid"] = blob["id"]
                blob["changed"] = True
                newtracks.append(blob)

        # Remaining tracks are now dead
        return newtracks, tracks