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

blobsbyid = {}
tracks = []
identifications = {}
inaturalistrecords = {}
taxondictionary = None
taxonnames = []

if len(sys.argv) < 2:
    rootfolder = "D:\AMT"
else:
    rootfolder = sys.argv[1]

if !os.path.exists(rootfolder):
    print("Usage: python ")
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