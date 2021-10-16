import os
import cv2
import csv
import sys

agecolors = [(0, 128, 0), (255, 0, 0), (255, 50, 50), (255, 100, 100), (255, 150, 150), (255, 200, 200), (0, 0, 255)]

if len(sys.argv) < 2:
    print("Usage: python CreateMovie.py directorypath")
    sys.exit()

foldername = sys.argv[1]
datafolder = os.path.join(foldername, "data")
blobfolder = os.path.join(datafolder, "blob")
amtblobfile = os.path.join(datafolder, "amt_blob.csv")
amttrackfile = os.path.join(datafolder, "amt_track.csv")
amtimagefile = os.path.join(datafolder, "amt_image.csv")
if os.path.isdir(blobfolder) and os.path.isfile(amtblobfile) and os.path.isfile(amtimagefile):

    identifications = None
    if os.path.isfile(amttrackfile):
        identifications = {}
        with open(amttrackfile, newline='') as trackfile:
            trackreader = csv.reader(trackfile, delimiter=',')
            next(trackreader)
            for track in trackreader:
                identifications[track[0]] = track[1]

    imageblobs = {}

    with open(amtblobfile, newline='') as bloblist:
        blobreader = csv.reader(bloblist, delimiter=',')
        headings = next(blobreader)
        itrackid = headings.index("trackid")
        iimageid = headings.index("imageid")
        ixcrop = headings.index("xcrop")
        iycrop = headings.index("ycrop")
        iwcrop = headings.index("wcrop")
        ihcrop = headings.index("hcrop")
        ixcenter = headings.index("xcenter")
        iycenter = headings.index("ycenter")

        for blob in blobreader:
            imageid = blob[iimageid]
            if imageid in imageblobs:
                blobs = imageblobs[imageid]
            else:
                blobs = []
                imageblobs[imageid] = blobs
            blobs.append(blob)

    moviewriter = cv2.VideoWriter(os.path.join(datafolder, "amt.avi"), cv2.VideoWriter_fourcc(*'DIVX'), 5, (3840, 2160))
    trails = {}

    with open(amtimagefile, newline='') as imagelist:
        imagereader = csv.reader(imagelist, delimiter=',')
        headings = next(imagereader)
        iid = headings.index("id")
        ifilename = headings.index("filename")

        for image in imagereader:
            id = image[iid]
            filepath = os.path.join(foldername, image[ifilename])
            img = cv2.imread(filepath)

            if id in imageblobs:
                for blob in imageblobs[id]:
                    trackid = blob[itrackid]
                    if identifications is not None and trackid in identifications:
                        label = identifications[trackid]
                    else:
                        label = str(trackid)
                    xcrop = int(blob[ixcrop])
                    ycrop = int(blob[iycrop])
                    wcrop = int(blob[iwcrop])
                    hcrop = int(blob[ihcrop])
                    xcenter = int(blob[ixcenter])
                    ycenter = int(blob[iycenter])

                    cv2.rectangle(img, (xcrop, ycrop), (xcrop + wcrop, ycrop + hcrop), agecolors[0], 2)
                    if ycrop < 30:
                        cv2.putText(img, label, (xcrop, ycrop + hcrop + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, agecolors[0], 2, cv2.LINE_AA)
                    else:
                        cv2.putText(img, label, (xcrop, ycrop - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, agecolors[0], 2, cv2.LINE_AA)

                    if trackid in trails:
                        trail = trails[trackid]
                        x1, y1 = xcenter, ycenter
                        age = 0
                        while age < len(trail) and age < 5:
                            x2, y2 = trail[age]
                            cv2.line(img, (x1, y1), (x2, y2), agecolors[age + 1], 2, cv2.LINE_AA)
                            x1, y1 = x2, y2
                            age += 1
                    else:
                        trail = []
                        trails[trackid] = trail
                    trail.insert(0, (xcenter, ycenter))
                    if len(trail) > 5:
                        trail = trail[0:5]

            moviewriter.write(img)

        moviewriter.release()
