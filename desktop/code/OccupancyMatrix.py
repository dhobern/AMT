import math
import csv
import os
import sys
import shutil
import time
import yaml
import pandas
from datetime import datetime

foldername = None
blobfolder = None
images = {}

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

taxondictionary = None
taxonnames = {}

if len(sys.argv) < 3:
    print("Usage: python OccupancyMatrix.py directorypath [taxondictionary]")
    sys.exit()

taxondictionary = sys.argv[2]
if os.path.isfile(taxondictionary):
    with open(taxondictionary, newline='') as taxon_file:
        taxon_reader = csv.reader(taxon_file, delimiter=',')
        taxonheadings = next(taxon_reader)
        for line in taxon_reader:
            taxonnames[line[0].strip()] = line

foldername = sys.argv[1]
datafolder = os.path.join(foldername, "data")
if os.path.isdir(datafolder):
    imgfile = os.path.join(datafolder, "amt_image.csv")
    blobfile = os.path.join(datafolder, "amt_blob.csv")
    trackfile = os.path.join(datafolder, "amt_track.csv")
    matrixfile = os.path.join(datafolder, "amt_matrix.csv")
    if os.path.isfile(imgfile) and os.path.isfile(blobfile) and os.path.isfile(trackfile):
        with open(imgfile, newline='', encoding="utf8") as imglist, open(blobfile, newline='', encoding="utf8") as bloblist, open(trackfile, newline='', encoding="utf8") as tracklist, open(matrixfile, 'w', newline='', encoding="utf8") as matrixlist:
            imgreader = csv.reader(imglist, delimiter=',')
            imgheadings = next(imgreader)
            iid = imgheadings.index("id")
            idatetime = imgheadings.index("datetime")
            blobreader = csv.reader(bloblist, delimiter=',')
            blobheadings = next(blobreader)
            bid = blobheadings.index("id")
            bimageid = blobheadings.index("imageid")
            bx = blobheadings.index("x")
            by = blobheadings.index("y")
            bw = blobheadings.index("w")
            bh = blobheadings.index("h")
            trackreader = csv.reader(tracklist, delimiter=',')
            trackheadings = next(trackreader)
            tid = trackheadings.index("id")
            matrixwriter = csv.writer(matrixlist, delimiter=',')

            matrix = pandas.DataFrame()

            tracks = {}

            for track in trackreader:
                tracks[track[tid]]= track

            blobs = {}

            for blob in blobreader:
                if blob[bimageid] not in blobs:
                    blobs[blob[bimageid]] = []
                blobs[blob[bimageid]].append(blob)

            for img in imgreader:


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

            if len(tracks) == 0:
                print("No tracks to edit")
                exit()

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