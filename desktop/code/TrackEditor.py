from tkinter import *
from tkinter import ttk
from ttkwidgets.autocomplete import AutocompleteEntry
from PIL import ImageTk,Image  
from functools import partial
import math
import csv
import os
import shutil
import time
import yaml
from datetime import datetime
import pyinaturalist
import webbrowser

metadata = None

inaturalist_username = None
inaturalist_password = None
inaturalist_app_id = None
inaturalist_app_secret = None
inaturalist_token = None

try:
    from iNaturalistCredentials  import *
except ImportError:
    pass

foldername = None
blobfolder = None
images = {}

canvas = None
container = None
grey = "#F0F0F0"
blue = "#E8E8FF"
red = "#FFD0D0"
green = "#D0FFD0"
trackheadings = ["id", "identification", "inaturalistID", "inaturalistRG", "inaturalistTaxon"]

class Track:
    def __init__(self, id, blobs, identification, inatid, inatrg, inattaxon, deleted = False):
        self.id = id
        self.blobs = blobs
        self.identification = identification
        self.averagesize = 1
        self.inaturalist_id = inatid
        self.inaturalist_rg = inatrg
        self.inaturalist_taxon = inattaxon
        self.deleted = deleted

    def setaveragesize(self):
        total = 0
        for blob in self.blobs:
            total += int(blob[iblobsize])
        self.averagesize = math.floor(math.sqrt(total / len(self.blobs)))

class TrackCanvas(Canvas):
    def __init__(self, container, tracks, headings, taxonnames, blobsize, rows, **kwargs):
        super().__init__(container, **kwargs)
        self.newtrackid = -1
        self.tracktolink = -1
        self.sort = "start time"
        self.filter = None
        self.tracks = tracks
        self.tracksbyid = {}
        self.setdisplaytracks()
        self.blobsize = blobsize
        self.parent = container

        if rows > len(tracks):
            self.rows = len(tracks)
        else:
            self.rows = rows
        self.startindex = 0
        self.iimagename = headings.index("filename")
        self.itrackid = headings.index("trackid")
        self.iblobid = headings.index("id")
        self.width = 0
        self.height = 0
        self.tframeheights = [0] * self.rows

        self.tframes = []
        for i in range(self.rows):
            track = self.tracks[self.displaytracks[self.startindex + i]]
            tframe = TrackFrame(self, track, blobsize, self.iimagename, self.iblobid, headings, taxonnames, odd = bool(i % 2))
            tframe.grid_propagate(False)
            self.tframes.append(tframe)

        self.focusontframe(self.tframes[0])

    def filtertracks(self, var, clear):
        if clear:
            self.filter = None
            var.set("")
        else:
            self.filter = var.get().strip()
        self.resetdisplaytracks()

    def sorttracks(self, var, *args):
        self.sort = var.get()
        self.resetdisplaytracks()

    def setdisplaytracks(self):
        if self.tracktolink >= 0:
            self.tframes[self.tracktolink].linking = False
            self.tracktolink = -1
        self.displaytracks = []
        self.startindex = 0
        for i in range(len(self.tracks)):
            if self.filter is None or (len(self.filter) > 0 and self.tracks[i].identification.startswith(self.filter)) or self.filter == self.tracks[i].identification:
                self.displaytracks.append(i)
        if self.sort == "blob size":
            self.displaytracks.sort(key=lambda x:-self.tracks[x].averagesize)
        elif self.sort == "identification":
            self.displaytracks.sort(key=lambda x:(self.tracks[x].identification if self.tracks[x].identification != "" else "ZZZZZ"))

    def resetdisplaytracks(self):
        self.setdisplaytracks()
        self.refreshtframes()

    def resize(self, width):
        if width != self.width or self.height == 0:
            self.width = width
            self.height = 0
            rangeend = self.rows
            if self.startindex + self.rows > len(self.displaytracks):
                rangeend = len(self.displaytracks) - self.startindex
            for i in range(rangeend):
                tframe = self.tframes[i]
                self.tframeheights[i] = tframe.calculateheight(self.width)
                tframe.place(x=0, y=self.height)
                self.height += self.tframeheights[i]
            self.configure(height = self.height, width = self.width)

    def bbox(self, tagOrId = None):
        return (0, 0, self.width, self.height)

    def trackindexfromid(self, trackid):
        if self.startindex + self.rows > len(self.displaytracks):
            rangeend = len(self.displaytracks) - self.startindex
        else:
            rangeend = self.rows
        for i in range(rangeend):
            if self.tracks[self.displaytracks[self.startindex + i]].id == trackid:
                return i
        return -1

    def joinwithprevious(self, trackid):
        trackindex = self.trackindexfromid(trackid)
        if trackindex == 0:
            self.prevrow()
        elif trackindex > 0:
            self.combinetracks(trackindex - 1, trackindex)

    def combinetracks(self, targetindex, sourceindex):
        if targetindex > sourceindex:
            targetindex, sourceindex = sourceindex, targetindex
        sourcetrack = self.tracks[self.displaytracks[self.startindex + sourceindex]]
        source = sourcetrack.blobs
        targettrack = self.tracks[self.displaytracks[self.startindex + targetindex]]
        target = targettrack.blobs
        trackid = targettrack.id
        for blob in source:
            blob[itrackid] = trackid
            target.append(blob)
        targettrack.setaveragesize()
        if len(targettrack.inaturalist_id) == 0:
            targettrack.inaturalist_id = sourcetrack.inaturalist_id
            targettrack.inaturalist_rg = sourcetrack.inaturalist_rg
            targettrack.inaturalist_taxon = sourcetrack.inaturalist_taxon
        displaytrackindex = self.startindex + sourceindex
        actualtrackindex = self.displaytracks[displaytrackindex]
        self.tracks.pop(actualtrackindex)
        self.displaytracks.pop(displaytrackindex)
        for i in range(len(self.displaytracks)):
            if self.displaytracks[i] >= actualtrackindex:
                self.displaytracks[i] -= 1
        if self.startindex + self.rows > len(self.displaytracks):
            rangeend = len(self.displaytracks) - self.startindex
        else:
            rangeend = self.rows
        for i in range(targetindex, rangeend):
            self.tframes[i].settrack(self.tracks[self.displaytracks[self.startindex + i]])
        self.height = 0
        self.resize(self.width)
        resizecontainer(None)

    def splitat(self, trackid, blobid):
        trackindex = self.trackindexfromid(trackid)
        if trackindex >= 0:
            newblobs = []
            blobindex = -1
            newtrack = None
            track = self.tracks[self.displaytracks[self.startindex + trackindex]]
            blobs = track.blobs
            for b in range(len(blobs)):
                if blobs[b][self.iblobid] == blobid:
                    blobindex = b 
                    break
            while blobindex < len(blobs):
                blob = blobs.pop(blobindex)
                blob[itrackid] = self.newtrackid
                newblobs.append(blob)
            track.setaveragesize()
            newtrack = Track(self.newtrackid, newblobs, track.identification, track.inaturalist_id, track.inaturalist_rg, track.inaturalist_taxon, track.deleted)
            newtrack.setaveragesize()
            self.newtrackid -= 1
            indexbeforeinsertion = self.displaytracks[self.startindex + trackindex]
            for i in range(len(self.displaytracks)):
                if self.displaytracks[i] > indexbeforeinsertion:
                    self.displaytracks[i] += 1
            self.tracks.insert(self.displaytracks[self.startindex + trackindex] + 1, newtrack)
            self.displaytracks.insert(self.startindex + trackindex + 1, self.displaytracks[self.startindex + trackindex] + 1)
            rangeend = self.rows
            if self.startindex + rangeend > len(self.displaytracks):
                rangeend = len(self.displaytracks) - self.startindex
            for i in range(trackindex, rangeend):
                self.tframes[i].settrack(self.tracks[self.displaytracks[self.startindex + i]])
            self.height = 0
            self.resize(self.width)
            resizecontainer(None)

    def nextpage(self):
        if self.tracktolink >= 0:
            self.tframes[self.tracktolink].linking = False
            self.tracktolink = -1
        if self.startindex + self.rows < len(self.displaytracks):
            self.startindex += self.rows - 1
            self.refreshtframes()

    def prevpage(self):
        if self.tracktolink >= 0:
            self.tframes[self.tracktolink].linking = False
            self.tracktolink = -1
        if self.startindex > 0:
            self.startindex -= self.rows - 1
            if self.startindex < 0:
                self.startindex = 0
            self.refreshtframes()

    def prevrow(self):
        if self.tracktolink == self.rows - 1:
            self.tframes[self.tracktolink].linking = False
            self.tracktolink = -1
        elif self.tracktolink >= 0:
            self.tframes[self.tracktolink].linking = False
            self.tracktolink += 1
            self.tframes[self.tracktolink].linking = True
        if self.startindex > 0:
            self.startindex -= 1
            self.refreshtframes()

    def refreshtframes(self):
        canvas.yview_moveto(0)
        rangeend = self.rows
        if self.startindex + self.rows > len(self.displaytracks):
            rangeend = len(self.displaytracks) - self.startindex
        for i in range(rangeend):
            track = self.tracks[self.displaytracks[i + self.startindex]]
            self.tframes[i].settrack(track)
        for i in range(rangeend, self.rows):
            self.tframes[i].settrack(None)
        self.height = 0
        self.resize(self.width)
        resizecontainer(None)
        self.focusontframe(self.tframes[0])

    def linktracks(self, trackid):
        trackindex = self.trackindexfromid(trackid)
        if self.tracktolink < 0:
            self.tracktolink = trackindex
            return True
        if trackindex == self.tracktolink:
            self.tracktolink = -1
            self.tframes[self.tracktolink].linking = False
            return False

        self.combinetracks(self.tracktolink, trackindex)
        self.tframes[self.tracktolink].linking = False
        self.tframes[self.tracktolink].setstyle()
        self.tracktolink = -1
        return False

    def tabforward(self, tframe, *args):
        for t in range(len(self.tframes)):
            if self.tframes[t] == tframe:
                newtframe = self.tframes[0 if t == len(self.tframes) - 1 else t + 1]
                self.focusontframe(newtframe)
        return 'break'

    def tabbackward(self, tframe, *args):
        for t in range(len(self.tframes)):
            if self.tframes[t] == tframe:
                newtframe = self.tframes[len(self.tframes) - 1 if t == 0 else t - 1]
                self.focusontframe(newtframe)
        return 'break'
    
    def focusontframe(self, tframe):
        tframe.identify.focus_set()
        if self.height > 0:
            spaceabove = 0
            for t in range(len(self.tframes)):
                if tframe != self.tframes[t]:
                    spaceabove += self.tframeheights[t]
                else:
                    break
            if spaceabove > self.height - self.parent.winfo_height():
                spaceabove = self.height - self.parent.winfo_height()
            canvas.yview_moveto(spaceabove / self.height)

class TrackFrame(ttk.Frame):
    def __init__(self, parent, track, blobsize, iimagename, iblobid, headings, taxonnames, odd, **kwargs):
        self.track = None
        self.headings = headings
        self.width = 0
        self.height = 0
        self.odd = odd
        self.parent = parent
        self.linking = False
        self.taxonnames = taxonnames
        self.blobsize = blobsize
        self.iimagename = iimagename
        self.iblobid = iblobid
        if kwargs is None:
            kwargs = {}
        super().__init__(parent, **kwargs)

        self.taxonname = StringVar(self, "", "identification" + str(self))

        callback = self.register(self.identificationchanged)

        self.options = ttk.Frame(self, padding = "5 5 5 5")
        self.options.grid(column=0, row=0, sticky=(N, W, E))
        self.label = ttk.Label(self.options, width = 10, anchor = CENTER, text = "")
        self.label.grid(column = 0, row = 0, sticky=(N, W, S))
        self.link = ttk.Button(self.options, text = "🔗", command=self.linktracks)
        self.link.grid(column = 1, row = 0, sticky=(N, W, S))
        self.identify = AutocompleteEntry(self.options, width = 30, textvariable=self.taxonname, validate="focusout", validatecommand=(callback, '%P'), completevalues=taxonnames)
        self.identify.grid(column = 2, row = 0, sticky=(N, W, S))
        self.identify.bind("<Tab>", partial(parent.tabforward, self))
        self.identify.bind("<Shift-Tab>", partial(parent.tabbackward, self))
        i = 0
        for t in ["Insecta", "Coleoptera", "Diptera", "Hymenoptera", "Lepidoptera", "Trichoptera", "Hemiptera", "Tortricidae", "Oecophoridae", "Formicidae", "Araneae"]:
            tbutton = ttk.Button(self.options, width = 6, text=t[0:3], command = partial(self.setidentification, t))
            tbutton.grid(column = 3 + i, row = 0, sticky = (N, W, S))
            i += 1
        self.details = ttk.Button(self.options, text="👁", command=self.viewdetails)
        self.details.grid(column = 3 + i, row = 0, sticky=(N, W, S))
        self.trash = ttk.Button(self.options, text="🗑", command=self.deletetrack)
        self.trash.grid(column = 4 + i, row = 0, sticky=(N, W, S))
        self.inat = ttk.Button(self.options, text="🐦", command=self.sendtoinaturalist)
        self.inat.grid(column = 5 + i, row = 0, sticky=(N, W, S))
        self.bframe = BlobFrame(self, None, blobsize, iimagename, iblobid, odd)
        self.bframe.grid(column = 0, row = 1, sticky=(N, W, E, S))
        self.bframe.grid_propagate(False)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.settrack(track)
        self.setstyle()

    def calculateheight(self, width):
        if width != self.width or self.height == 0:
            self.width = width
            self.height = self.bframe.calculateheight(width) + self.options.winfo_height()
            self.configure(width=self.width, height=self.height)
        return self.height
    
    def joinwithprevious(self):
        self.parent.joinwithprevious(self.track.id)

    def splitat(self, blobid):
        self.track.identification = self.taxonname.get()
        self.parent.splitat(self.track.id, blobid)

    def deletetrack(self):
        self.track.deleted = not self.track.deleted
        self.setstyle()  

    def sendtoinaturalist(self):
        global root, inaturalist_token, metadata
        if len(self.track.inaturalist_id) > 0:
            webbrowser.open('https://inaturalist.ala.org.au/observations/' + self.track.inaturalist_id, new=2)
        elif len(self.track.identification) > 0:
            if inaturalist_token is None:
                global inaturalist_username, inaturalist_password, inaturalist_app_id, inaturalist_app_secret
                inaturalist_token = pyinaturalist.get_access_token(username=inaturalist_username, password=inaturalist_password, app_id=inaturalist_app_id, app_secret=inaturalist_app_secret)
            if metadata is None:
                metadata = readamtmetadata()
            if inaturalist_token is not None and metadata is not None:
                d = iNaturalistDialog(root, self, self.blobsize, self.iimagename, self.iblobid, self.track.blobs, metadata, inaturalist_token, self.track.identification)
                root.wait_window(d.top)
            if len(self.track.inaturalist_id) > 0:
                global datafolder, tracks, trackheadings, headings, taxondictionary, taxonnames, taxonmaster
                savetracks(datafolder, tracks, trackheadings, headings, taxondictionary, taxonnames, taxonmaster)

    def viewdetails(self):
        global root
        d = DetailsDialog(root, self)
        root.wait_window(d.top)

    def linktracks(self):
        self.linking = self.parent.linktracks(self.track.id)
        self.setstyle()

    def settrack(self, track):
        if self.track is not None:
            self.track.identification = self.taxonname.get()
        self.track = track
        if track is None:
            self.label.configure(text = "")
            self.taxonname.set("")
            self.bframe.setblobs(None)
        else:
            self.label.configure(text = str(track.id) + " (" + str(track.averagesize)  + ")")
            self.taxonname.set(self.track.identification)
            self.bframe.setblobs(track.blobs)
        self.height = 0
        self.calculateheight(self.width)
        self.setstyle()

    def setstyle(self):
        deleted = False if self.track is None else self.track.deleted
        stylename = "Deleted.TFrame" if deleted else "Linking.TFrame" if self.linking else "Odd.TFrame" if self.odd else "Even.TFrame"
        labelstylename = "Deleted.TLabel" if deleted else "Linking.TLabel" if self.linking else "Odd.TLabel" if self.odd else "Even.TLabel"
        self.configure(style=stylename)
        self.options.configure(style=stylename)
        self.label.configure(style=labelstylename)
        self.bframe.configure(style=stylename)

    def setidentification(self, identification):
        self.taxonname.set(identification)
        self.track.identification = identification
        return True

    def identificationchanged(self, input):
        if self.track is not None:
            self.track.identification = input.strip()
            if self.track.identification not in self.taxonnames:
                taxonnames.append(self.track.identification)
                taxonnames.sort()
        return True

    def setinaturalistid(self, id):
        self.track.inaturalist_id = id

class BlobFrame(ttk.Frame):
    def __init__(self, container, blobs, blobsize, iimagename, iblobid, odd, mode="SplitJoin", **kwargs):
        self.blobs = [] if blobs is None else blobs
        self.blobsize = blobsize
        self.buttons = []
        self.width = 0
        self.height = 0
        self.blobsperrow = 10
        self.padx = 30
        self.pady = 10
        self.iimagename = iimagename
        self.iblobid = iblobid
        self.odd = odd
        self.mode = mode
        self.selected = []
        self.buttonlookup = {}
        padding = str(self.pady) + " " + str(self.pady) + " " + str(self.padx) + " " + str(self.padx)
        if kwargs is None:
            kwargs = {}
        kwargs["padding"] = padding
        super().__init__(container, **kwargs)
        self.loadblobs()

    def loadblobs(self):
        global images, blobfolder
        first = True
        self.buttons = []
        for widget in self.winfo_children():
            widget.destroy()
        for blob in self.blobs:
            if len(blob[self.iimagename]) > 0:
                imagefile = os.path.join(blobfolder, blob[self.iimagename])
                if imagefile in images:
                    img = images[imagefile]
                else:
                    if len(images) > 5000:
                        i = 0
                        keys = []
                        for k in images:
                            keys.append(k)
                            i += 1
                            if i == 1000:
                                break
                        for k in keys:
                            images.pop(k, None)

                    img = Image.open(imagefile)
                    size = img.size
                    if size[0] > self.blobsize or size[1] > self.blobsize:
                        scale = self.blobsize / (size[0] if size[0] > size[1] else size[1])
                        img = img.resize((int(float(size[0])*scale),int(float(size[1])*scale)))
                    img = ImageTk.PhotoImage(img)
                    images[imagefile] = img
                if self.mode == "SplitJoin":
                    command = partial(self.splitjoin, -1 if first else blob[self.iblobid])
                elif self.mode == "MultiSelect":
                    command = partial(self.multiselect, blob[self.iblobid])
                else:
                    command = partial(self.silentclick, blob)
                button = Button(self, width = self.blobsize, height = self.blobsize, bd=-3, background=grey if self.odd else blue, image=img, command=command)
                first = False
                self.buttons.append(button)
                self.buttonlookup[blob[self.iblobid]] = button
        self.arrangeblobs()

    def splitjoin(self, blobid):
        if blobid == -1:
            self._nametowidget(self.winfo_parent()).joinwithprevious()
        else:
            self._nametowidget(self.winfo_parent()).splitat(blobid)
    
    def multiselect(self, blobid):
        if blobid in self.selected:
            self.selected.remove(blobid)
            self.buttonlookup[blobid].configure(bg = grey if self.odd else blue)
        else:
            self.selected.append(blobid)
            self.buttonlookup[blobid].configure(bg = green)

    def silentclick(self, blob):
        pass

    def arrangeblobs(self):
        for b in range(len(self.buttons)):
            button = self.buttons[b]
            button.grid(row = math.floor(b/self.blobsperrow), column = b % self.blobsperrow, sticky=(N,W))

    def calculateheight(self, width):
        if width != self.width or self.height == 0:
            self.width = width
            blobsperrow = math.floor((width - 2 * self.padx) / self.blobsize)
            if blobsperrow != self.blobsperrow:
                if blobsperrow > 1:
                    self.blobsperrow = blobsperrow
                    self.arrangeblobs()
            self.height = math.ceil(len(self.buttons) / self.blobsperrow) * (self.blobsize + 2) + (2 * self.pady)
            self.configure(width=self.width, height=self.height)
        return self.height

    def setblobs(self, blobs):
        self.blobs = [] if blobs is None else blobs
        self.loadblobs()
        self.height = 0

class DetailsDialog:
    def __init__(self, root, tframe):
        self.tframe = tframe
        self.top = Toplevel(root)
        self.top.transient(root)
        self.top.grab_set()
        self.top.title("Track: " + str(tframe.track.id))
        self.blobindex = 0

        self.canvas = Canvas(self.top, width = 500, height = 500)
        self.canvas.grid(column=0, row=0, columnspan=2, sticky=(N, E, W, S))
        #self.canvas["bg"] = grey
        self.label = ttk.Label(self.top, width = 50, text="")
        self.label.grid(column = 2, row = 0, sticky=(N, E, W, S))
        self.prev = ttk.Button(self.top, text="Previous image", command=self.previous)
        self.prev.grid(column = 0, row = 1, sticky=(N, E, W, S))
        self.next = ttk.Button(self.top, text="Next image", command=self.next)
        self.next.grid(column = 1, row = 1, sticky=(N, E, W, S))
        self.cancel = ttk.Button(self.top, text="Cancel", command=self.cancel)
        self.cancel.grid(column = 2, row = 1, sticky=(N, E, W, S))
        self.showblob(self.blobindex)
        self.cancel.focus_set()

        self.top.columnconfigure(0, weight=1)
        self.top.columnconfigure(1, weight=1)
        self.top.rowconfigure(0, weight=1)

    def showblob(self, index):
        global blobfolder
        labeltext = ""
        blob = self.tframe.track.blobs[index]
        for i in range(len(self.tframe.track.blobs[index])):
            labeltext += self.tframe.headings[i] + ": " + str(blob[i]) + "\n"
        self.label.config(text=labeltext)
        if len(blob[self.tframe.iimagename]) > 0:
            imagefile = os.path.join(blobfolder, blob[self.tframe.iimagename])
            image = Image.open(imagefile)
            size = image.size
            if size[0] > 500 or size[1] > 500:
                scale = 500 / (size[0] if size[0] > size[1] else size[1])
                image = image.resize((int(float(size[0])*scale),int(float(size[1])*scale)))
            self.img = ImageTk.PhotoImage(image)
            self.canvas.create_image(250, 250, image=self.img, anchor=CENTER)

    def next(self, event=None):
        if self.blobindex < len(self.tframe.track.blobs) - 1:
            self.blobindex += 1
            self.showblob(self.blobindex)
 
    def previous(self, event=None):
        if self.blobindex > 0:
            self.blobindex -= 1
            self.showblob(self.blobindex)
 
    def cancel(self, event=None):
        self.top.destroy()

class iNaturalistDialog(ttk.Frame):
    def __init__(self, root, tframe, blobsize, iimagename, iblobid, blobs, metadata, token, identification, **kwargs):
        self.tframe = tframe
        self.top = Toplevel(root)
        self.top.transient(root)
        self.top.grab_set()
        self.top.title("Track: " + str(tframe.track.id))
        self.iimagename = iimagename
        self.blobs = blobs
        self.iblobid = iblobid
        self.metadata = metadata
        self.token = token
        self.identification = identification
        super().__init__(root, **kwargs)

        self.bframe = BlobFrame(self.top, None, blobsize, iimagename, iblobid, False, mode="MultiSelect")
        self.bframe.grid(column = 0, row = 0, columnspan=2, sticky=(N, W, E, S))
        self.bframe.grid_propagate(False)
        self.bframe.configure(width = 1000, height = 600)
        self.bframe.setblobs(self.blobs)
        self.info = ttk.Label(self.top, width = 50, text="")
        self.info.grid(column = 0, row = 1, columnspan = 2, sticky=(N, E, W, S))
        infotext = identification
        if "latitude" in metadata and "longitude" in metadata:
            infotext += " (" + str(abs(metadata["longitude"])) + (" E, " if metadata["longitude"] >= 0 else " W,") + str(abs(metadata["latitude"])) + (" N" if metadata["latitude"] >= 0 else " S")
            if "positional_accuracy" in metadata:
                infotext += ", " + str(metadata["positional_accuracy"]) + " metres accuracy"
            infotext += ")"
        self.info.config(text=infotext)
        self.description = ttk.Entry(self.top, width=50)
        self.description.insert(END, metadata["description"])
        self.description.grid(column = 0, row = 2, columnspan = 2, sticky=(N, E, W, S))
    
        self.cancel = ttk.Button(self.top, text="Cancel", command=self.cancel)
        self.cancel.grid(column = 0, row = 3, sticky=(N, E, W, S))
        self.create = ttk.Button(self.top, text="Submit", command=self.create)
        self.create.grid(column = 1, row = 3, sticky=(N, E, W, S))
        self.cancel.focus_set()

        self.width = 0
        self.height = 0

        self.top.columnconfigure(0, weight=1)
        self.top.columnconfigure(1, weight=1)
        self.top.rowconfigure(0, weight=1)

    def calculateheight(self, width):
        if width != self.width or self.height == 0:
            self.width = width
            self.height = self.bframe.calculateheight(width) + self.cancel.winfo_height()
            self.configure(width=self.width, height=self.height)
        return self.height

    def bbox(self, tagOrId = None):
        return (0, 0, self.width, self.height)

    def create(self, event=None):
        if len(self.bframe.selected) > 0:
            photoset = []
            for b in self.bframe.selected:
                for i in range(len(self.blobs)):
                    if self.blobs[i][self.iblobid] == b:
                        photoset.append(os.path.join(blobfolder, self.blobs[i][self.iimagename]))
            if len(photoset) > 0:
                response = pyinaturalist.create_observation(
                    species_guess=self.identification,
                    observed_on_string=track_datetime(self.blobs, self.iimagename),
                    time_zone='Sydney',
                    description=self.description.get(),
                    tag_list=self.metadata["tag_list"],
                    latitude=self.metadata["latitude"],
                    longitude=self.metadata["longitude"],
                    positional_accuracy=self.metadata["positional_accuracy"],
                    access_token=self.token,
                    photos=photoset
                )

                # Save the new observation ID
                self.tframe.setinaturalistid(str(response['id']))
        self.top.destroy()

    def cancel(self, event=None):
        self.top.destroy()

def track_datetime(blobs, iimagename):
    for b in blobs:
        if len(b[iimagename]) > 0:
            i = b[iimagename].index("_")
            if i >= 0:
                i += 1
                j = b[iimagename].index("_", i)
                if j >= 0:
                    return datetime.strptime(b[iimagename][i:j],"%Y%m%d%H%M%S")
    return None

def readamtmetadata():
    metadata = {}
    metadata["latitude"] = ""
    metadata["longitude"] = ""
    metadata["positional_accuracy"] = ""
    metadata["description"] = 'Image(s) from Automated Moth Trap - see <a href="https://amt.hobern.net/">AMT project overview</a>.'
    metadata["tag_list"] = 'AutomatedMothTrap'
    metadatafilename = os.path.join(foldername, "amt_metadata.yaml")
    if os.path.isfile(metadatafilename):
        yamlmetadata = yaml.load(open(metadatafilename), Loader=yaml.FullLoader)
        if "event" in yamlmetadata:
            event = yamlmetadata["event"]
            if "decimalLatitude" in event:
                metadata["latitude"] = event["decimalLatitude"]
            if "decimalLongitude" in event:
                metadata["longitude"] = event["decimalLongitude"]
            if "coordinateUncertaintyInMeters" in event:
                metadata["positional_accuracy"] = event["coordinateUncertaintyInMeters"]
        if "provenance" in yamlmetadata and "capture" in yamlmetadata["provenance"]:
            capture = yamlmetadata["provenance"]["capture"]
            hardware = []
            if "unitname" in capture:
                hardware.append("Unit: " + capture["unitname"])
                metadata["tag_list"] = metadata["tag_list"] + ", " + capture["unitname"]
            if "processor" in capture:
                hardware.append("Processor: " + capture["processor"])
            if "camera" in capture:
                hardware.append("Camera: " + capture["camera"])
            if "illumination" in capture:
                hardware.append("Illumination: " + capture["illumination"])
            if "uvlight" in capture:
                hardware.append("UV light: " + capture["uvlight"])
            if "mode" in capture:
                mode = capture["mode"]
                if mode == "Motion":
                    modetext = "motion detection by "
                elif mode == "TimeLapse":
                    modetext = "timelapse capture by "
                else:
                    modetext = ""

            if (len(hardware) > 0):
                metadata["description"] = 'Image(s) from ' + modetext + 'Automated Moth Trap (' + "; ".join(hardware) + ') - see <a href="https://amt.hobern.net/">AMT project overview</a>.'
    return metadata

def reporthierarchy(widget, indent = ""):
    print(indent + widget.winfo_class() + ": " + str(widget.winfo_width()) + "x" + str(widget.winfo_height()))
    for child in widget.winfo_children():
        reporthierarchy(child, indent + "  ")
        if child.winfo_class() == "Button" and len(child.winfo_children()) == 0:
            break

def resizecontainer(event):
    global container, canvas, trackviewer
    width = container.winfo_width() if event is None else event.width
    trackviewer.resize(width)
    canvas.configure(scrollregion=trackviewer.bbox("all"))
#    reporthierarchy(canvas)

def on_mousewheel(event):
    global canvas
    canvas.yview_scroll(-int(event.delta/24), UNITS)

def savetracks(datafolder, tracks, trackheadings, blobheadings, taxondictionary, taxonnames, taxonmaster):
    with open(os.path.join(datafolder, "amt_track.csv"), 'w', newline='', encoding="utf8") as amttrackfile, open(os.path.join(datafolder, "amt_blob.csv"), 'w', newline='', encoding="utf8") as amtblobfile:
        amttrackwriter = csv.writer(amttrackfile, delimiter=',')
        amtblobwriter = csv.writer(amtblobfile, delimiter=',')
        amttrackwriter.writerow(trackheadings)
        amtblobwriter.writerow(blobheadings)
        trackid = 1
        for track in tracks:
            if not track.deleted:
                amttrackwriter.writerow([str(trackid), track.identification, track.inaturalist_id, track.inaturalist_rg, track.inaturalist_taxon])
                for blob in track.blobs:
                    blob[itrackid] = trackid
                    amtblobwriter.writerow(blob)
                trackid += 1
    if taxondictionary is not None and len(taxonnames) > len(taxonmaster):
        save = False
        for track in tracks:
            if track.identification not in taxonmaster:
                taxonmaster.append(track.identification)
                save = True
        if save:
            taxonmaster.sort()
            shutil.copyfile(taxondictionary, taxondictionary + "." + datetime.now().strftime("%Y%m%d%H%M%S") + ".save")
            with open(taxondictionary, 'w', newline='', encoding="utf8") as taxonlist:
                for name in taxonmaster:
                    taxonlist.write("%s\n" % name)


blobsbyid = {}
tracks = []
identifications = {}
inaturalistrecords = {}
taxondictionary = None
taxonnames = []

if len(sys.argv) < 2:
    print("Usage: python TrackEditor.py directorypath [taxondictionary]")
    sys.exit()

if len(sys.argv) > 2:
    taxondictionary = sys.argv[2]
    if os.path.isfile(taxondictionary):
        taxonnames = []
        with open(taxondictionary, newline='') as taxonlist:
            lines = taxonlist.readlines()
            for line in lines:
                taxonnames.append(line.strip())

taxonmaster = taxonnames.copy()

foldername = sys.argv[1]
datafolder = os.path.join(foldername, "data")
if os.path.isdir(datafolder):
    blobfile = os.path.join(datafolder, "amt_blob.csv")
    if os.path.isfile(blobfile):
        shutil.copyfile(blobfile, os.path.join(datafolder, "amt_blob_backup_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".csv"))

        trackfile = os.path.join(datafolder, "amt_track.csv")
        if os.path.isfile(trackfile):
            shutil.copyfile(trackfile, os.path.join(datafolder, "amt_track_backup_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".csv"))
            with open(trackfile, newline='') as tracklist:
                trackreader = csv.reader(tracklist, delimiter=',')
                headings = next(trackreader)
                iid = headings.index("id")
                iidentification = headings.index("identification")
                if "inaturalistID" in headings:
                    iinatid = headings.index("inaturalistID")
                    iinatrg = headings.index("inaturalistRG")
                    iinattaxon = headings.index("inaturalistTaxon")
                else:
                    iinatid = -1
                    iinatrg = -1
                    iinattaxon = -1
                for track in trackreader:
                    identifications[track[iid]] = track[iidentification]
                    if iinatid >= 0 and len(track[iinatid]) > 0:
                        inaturalistrecords[track[iid]] = [track[iinatid], track[iinatrg] if iinatrg >= 0 else False, track[iinattaxon] if iinattaxon >=0 else ""]


        with open(blobfile, newline='') as bloblist:
            blobreader = csv.reader(bloblist, delimiter=',')
            headings = next(blobreader)
            itrackid = headings.index("trackid")
            iblobsize = headings.index("size")

            for blob in blobreader:
                trackid = blob[itrackid]
                if trackid in blobsbyid:
                    blobs = blobsbyid[trackid]
                else:
                    blobs = []
                    blobsbyid[trackid] = blobs
                    inat = ["", False, ""]
                    if trackid in identifications:
                        identification = identifications[trackid]
                        if trackid in inaturalistrecords:
                            inat = inaturalistrecords[trackid]
                    else:
                        identification = ""
                    tracks.append(Track(trackid, blobs, identification, inat[0], inat[1], inat[2]))
                blobs.append(blob)

            blobfolder = os.path.join(datafolder, "blob")

            for track in tracks:
                track.setaveragesize()
    else:
        print("Missing blob list: " + blobfile)
        exit()
else:
    print("Data folder not found: " + datafolder)
    exit()

root = Tk()
root.title("TrackEditor: " + foldername)

s = ttk.Style()
s.configure("Odd.TFrame", background=grey)
s.configure("Even.TFrame", background=blue)
s.configure("Deleted.TFrame", background=red)
s.configure("Linking.TFrame", background=green)
s.configure("Odd.TLabel", background=grey)
s.configure("Even.TLabel", background=blue)
s.configure("Deleted.TLabel", background=red)
s.configure("Linking.TLabel", background=green)

menu = ttk.Frame(root, padding="5 5 5 5")
menu.grid(column=0, row=0, sticky=(N, W, E))
container = ttk.Frame(root)
container.grid(column=0, row=1, sticky=(N, W, E, S))
canvas = Canvas(container)
canvas.grid(column=0, row=1, sticky=(N, W, E, S))
canvas["bg"] = grey
scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
scrollbar.grid(column=1, row=1, sticky=(N, E, S))
trackviewer = TrackCanvas(canvas, tracks, headings, taxonnames, blobsize = 100, rows = 12)
canvas.create_window((0, 0), window=trackviewer, anchor="nw")
container.bind("<Configure>", resizecontainer)
canvas.configure(yscrollcommand=scrollbar.set, yscrollincrement="10")
canvas.bind_all("<MouseWheel>", on_mousewheel)

filterlabel = ttk.Label(menu, text="Filter by identification", width=20)
filterlabel.grid(column=0, row=0, sticky=(N, E))
filtervar = StringVar()
filtervar.set("")
filtertext = AutocompleteEntry(menu, text="", width=30, textvariable=filtervar, completevalues=taxonnames)
filtertext.grid(column=1, row=0, sticky=(N, E))
filterapply = ttk.Button(menu, text = "Apply", command=partial(trackviewer.filtertracks, filtervar, False))
filterapply.grid(column=2, row=0, sticky=(N, E))
filterclear = ttk.Button(menu, text = "Clear", command=partial(trackviewer.filtertracks, filtervar, True))
filterclear.grid(column=3, row=0, sticky=(N, E))
sortoptions = ["start time", "blob size", "identification"]
sorttype = StringVar()
sorttype.set(sortoptions[0])
sorttype.trace("w", partial(trackviewer.sorttracks, sorttype))
sortdropdown = OptionMenu(menu, sorttype, *sortoptions)
sortdropdown.grid(column=4, row=0, sticky=(N, E))
prevpage = ttk.Button(menu, text="Prev", command=trackviewer.prevpage, padding="5 5 5 5")
prevpage.grid(column=5, row=0, sticky=(N, E))
nextpage = ttk.Button(menu, text="Next", command=trackviewer.nextpage, padding="5 5 5 5")
nextpage.grid(column=6, row=0, sticky=(N, E))
save = ttk.Button(menu, text="Save", command=partial(savetracks, datafolder, tracks, trackheadings, headings, taxondictionary, taxonnames, taxonmaster), padding="5 5 5 5")
save.grid(column=7, row=0, sticky=(N, E))

root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
container.columnconfigure(0, weight=1)
container.rowconfigure(1, weight=1)
container.rowconfigure(1, weight=1)

root.mainloop()