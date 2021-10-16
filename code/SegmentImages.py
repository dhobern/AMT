import os
import re
import cv2
import csv
import math
import shutil
import json
from skimage.exposure import is_low_contrast

from amt_blobdetector import AMTBlobDetector
from amt_tracker import AMTTracker

def readconfig(path):
    with open(path) as file:
        data = json.load(file)
    return data

def writerecord(writer, record, headings):
    row = []
    for h in headings:
        if h in record:
            row.append(record[h])
        else:
            row.append("")
    writer.writerow(row)

dt_pattern = re.compile("^20[0-9]{12}")
def getdatetime(filename):
    result = dt_pattern.search(filename)
    if result is not None:
        return result.group(0)
    return "<UNKNOWN>"

temp_pattern = re.compile("TempC_([0-9.]+)")
def gettemperature(filename):
    result = temp_pattern.search(filename)
    if result is not None:
        return result.group(1)
    return "<UNKNOWN>"

humid_pattern = re.compile("Humid_([0-9.]+[0-9])")
def gethumidity(filename):
    result = humid_pattern.search(filename)
    if result is not None:
        return result.group(1)
    return "<UNKNOWN>"

def ishighcontrast(image, blob, threshold):
    image = cv2.resize(blob["blobimage"], (450, 450))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return not is_low_contrast(gray, threshold)

def getcount(hist, size, color, mindiff, maxdiff):
    count = 0
    for r in range(size):
        for g in range(size):
            for b in range(size):
                if (color == "R" and r >= g + b + mindiff and abs(g - b) <= maxdiff) or \
                    (color == "G" and g >= r + b + mindiff and abs(r - b) <= maxdiff) or \
                    (color == "B" and b >= r + g + mindiff and abs(r - g) <= maxdiff) or \
                    (color == "C" and r <= g + b - size - mindiff + 1 and abs(g - b) <= maxdiff) or \
                    (color == "M" and g <= r + b - size - mindiff + 1 and abs(r - b) <= maxdiff) or \
                    (color == "Y" and b <= r + g - size - mindiff + 1 and abs(r - g) <= maxdiff):
                        count += hist[b][g][r]
    return count    

def reportcolors(image):
    h, w, channels = image.shape
    pixels = h * w
    size = 3
    mindiff = 1 
    maxdiff = 1
    threshold = 0.02
    hist = cv2.calcHist([image], [0, 1, 2], None, [size, size, size], [0, 256, 0, 256, 0, 256])
    colors = ""
    for c in [ "R", "G", "B", "C", "M", "Y" ]:
        if getcount(hist, size, c, mindiff, maxdiff) / pixels > threshold:
            colors += c
    return colors

def isinteresting(image, blob, width, height, threshold):
    if not ishighcontrast(image, blob, threshold):
        return False
    if (blob["xcrop"] > 0 and blob["xcrop"] + blob["wcrop"] < width):
        return True
    elif (blob["ycrop"] > 0 and blob["ycrop"] + blob["hcrop"] < height):
        return True
    elif blob["h"] / blob["w"] < 2:
        return True
    return False

config_filename = "../config/AMT_config.json"

amtimgheadings = [ "id", "datetime", "filename", "temperature", "humidity" ]
amtblobheadings = [ "id", "imageid", "filename", "x", "y", "w", "h", "xcrop", "ycrop", "wcrop", "hcrop", "xcenter", "ycenter", "size", "illumination", "changed", "colors", "trackid", "cost", "weights", "direction", "delay" ]

conf = readconfig(config_filename)
basefolder = conf['datapath']

threshold = conf['threshold']
savingmarked = conf['savemarked']
savingmovie = conf['savemovie']
markchanged = conf['markchanged']
moviewriter = None

agecolors = [(0, 128, 0), (255, 0, 0), (255, 50, 50), (255, 100, 100), (255, 150, 150), (255, 200, 200), (0, 0, 255)]

p = re.compile("^20[-0-9]*$")
for f in os.listdir(basefolder):
    print(f)
    if os.path.isdir(os.path.join(basefolder, f)) and p.match(f) and (conf['force'] or not os.path.isdir(os.path.join(basefolder, f, "data"))):
        folder = os.path.join(basefolder, f)
        datafolder = os.path.join(folder, "data")
        markedfolder = os.path.join(datafolder, "marked")
        blobfolder = os.path.join(datafolder, "blob")

        if os.path.isdir(datafolder) and conf['force']:
            shutil.rmtree(datafolder)
        os.mkdir(datafolder)
        os.mkdir(blobfolder)
        if savingmarked:
            os.mkdir(markedfolder)
        if savingmovie:
            moviewriter = cv2.VideoWriter(os.path.join(datafolder, "amt.avi"), cv2.VideoWriter_fourcc(*'DIVX'), 5, (3840, 2160))
            trails = {}

        identifications = None
        trackfilename = os.path.join(folder, "amt_track.csv")
        if os.path.isfile(trackfilename):
            identifications = {}
            with open(trackfilename, newline='') as trackfile:
                trackreader = csv.reader(trackfile, delimiter=',')
                next(trackreader)
                for track in trackreader:
                    identifications[int(track[0])] = track[1]

        with open(os.path.join(datafolder, "amt_image.csv"), 'w', newline='', encoding="utf8") as amtimgfile, open(os.path.join(datafolder, "amt_blob.csv"), 'w', newline='', encoding="utf8") as amtblobfile:
            amtimgwriter = csv.writer(amtimgfile, delimiter=',')
            amtblobwriter = csv.writer(amtblobfile, delimiter=',')
            amtimgwriter.writerow(amtimgheadings)
            amtblobwriter.writerow(amtblobheadings)
        
            imageid = 0
            blobid = 0
            bl = None
            tr = None
            tracks = []
            for filename in os.listdir(folder):
                if filename.endswith("jpg"):
                    filepath = os.path.join(folder, filename)

                    if bl is None:
                        bl = AMTBlobDetector(conf)
                    if tr is None:
                        tr = AMTTracker(conf)

                    image = cv2.imread(filepath)
                    height, width, channels = image.shape
                    imageid += 1
                    imagerec = {}
                    imagerec["id"] = imageid
                    imagerec["datetime"] = getdatetime(filename)
                    imagerec["filename"] = filename
                    imagerec["temperature"] = gettemperature(filename)
                    imagerec["humidity"] = gethumidity(filename)
                    writerecord(amtimgwriter, imagerec, amtimgheadings)
                    print(filename + ": " + str(height) + " x " + str(width) + " x " + str(channels) + " " + imagerec["datetime"] + " " + imagerec["temperature"] + " " + imagerec["humidity"])

                    startid = 0
                    count, blobs, binary = bl.findblobs(image, imageid)

                    b = 0
                    while b < len(blobs):
                        if isinteresting(image, blobs[b], width, height, threshold):
                            blobid += 1
                            blobs[b]["id"] = blobid
                            b += 1
                        else:
                            blobs.pop(b)

                    tracks, deadtracks = tr.managetracks(tracks, blobs)

                    if savingmarked or savingmovie:
                        imagenew = image.copy()

                    for blob in tracks:
                        if savingmarked:
                            cv2.rectangle(imagenew, (blob["xcrop"], blob["ycrop"]), (blob["xcrop"] + blob["wcrop"], blob["ycrop"] + blob["hcrop"]), agecolors[blob["age"]], 2)
                            cost = str(blob["cost"])
                            if len(cost) > 5:
                                cost = cost[0:5]
                            if identifications is not None:
                                if blob["trackid"] in identifications:
                                    identification = identifications[blob["trackid"]]
                                else:
                                    identification = "Unknown"
                                if blob["ycrop"] < 30:
                                    cv2.putText(imagenew, identification, (blob["xcrop"], blob["ycrop"] + blob["hcrop"] + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, agecolors[blob["age"]], 2, cv2.LINE_AA)
                                else:
                                    cv2.putText(imagenew, identification, (blob["xcrop"], blob["ycrop"] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, agecolors[blob["age"]], 2, cv2.LINE_AA)
                            else:
                                labeltext = str(blob["trackid"]) + ": " + str(blob["id"]) + " (" + cost + ") / " + blob["colors"] 
                                if blob["ycrop"] < 60:
                                    cv2.putText(imagenew, labeltext, (blob["xcrop"], blob["ycrop"] + blob["hcrop"] + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, agecolors[blob["age"]], 2, cv2.LINE_AA)
                                    cv2.putText(imagenew, "{" + blob["weights"] + "}", (blob["xcrop"], blob["ycrop"] + blob["hcrop"] + 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, agecolors[blob["age"]], 2, cv2.LINE_AA)
                                else:
                                    cv2.putText(imagenew, labeltext, (blob["xcrop"], blob["ycrop"] - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, agecolors[blob["age"]], 2, cv2.LINE_AA)
                                    cv2.putText(imagenew, "{" + blob["weights"] + "}", (blob["xcrop"], blob["ycrop"] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, agecolors[blob["age"]], 2, cv2.LINE_AA)

                            if blob["trackid"] in trails:
                                trail = trails[blob["trackid"]]
                                x1, y1 = blob["xcenter"], blob["ycenter"]
                                age = 0
                                while age < len(trail) and age < 5:
                                    x2, y2 = trail[age]
                                    cv2.line(imagenew, (x1, y1), (x2, y2), agecolors[age + 1], 2, cv2.LINE_AA)
                                    x1, y1 = x2, y2
                                    age += 1
                            else:
                                trail = []
                                trails[blob["trackid"]] = trail
                            trail.insert(0, (blob["xcenter"], blob["ycenter"]))
                            if len(trail) > 5:
                                trail = trail[0:5]

                        if blob["age"] == 0:

                            if blob["changed"]:
                                blob["filename"] = str(blob["trackid"]) + "_" + imagerec["datetime"] + "_" + str(blobid) + ".jpg"
                                cv2.imwrite(os.path.join(blobfolder, blob["filename"]), blob["blobimage"])

                            writerecord(amtblobwriter, blob, amtblobheadings)

                            if markchanged:
                                if blob["changed"]:
                                    cv2.rectangle(blob["blobimage"], (2, 2), (w - 2, h - 2), (0, 255, 0), 2)
                                else:
                                    cv2.rectangle(blob["blobimage"], (2, 2), (w - 2, h - 2), (255, 0, 0), 2)

                    if savingmarked:
                        cv2.imwrite(os.path.join(markedfolder, "new" + filename), imagenew)

                    if savingmovie:
                        moviewriter.write(imagenew)

            if savingmovie:
                moviewriter.release()

