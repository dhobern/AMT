import os
import sys
import re
import cv2
import numpy as np

if len(sys.argv) < 2:
    print("Usage: python " + sys.argv[0] + " directorypath [fps [start-end]]] ")
    sys.exit()

if len(sys.argv) > 2:
    fps = int(sys.argv[2])
else:
    fps = 15

moviename = "AMT_" + str(fps) + ".avi"

startstring = None
endstring = None
include = True
if len(sys.argv) > 3:
    include = False
    moviename = "AMT_" + str(fps) + "_" + sys.argv[3] + ".avi"
    startstring, endstring = sys.argv[3].split("-")

p = re.compile("^20[-0-9]*.*jpg$")
foldername = sys.argv[1]
moviewriter = None

for filename in os.listdir(foldername):
    if filename.lower().endswith("jpg"):
        if startstring is not None and filename[0:len(startstring)] >= startstring:
            startstring = None
            include = True
        if endstring is not None and filename[0:len(endstring)] > endstring:
            endstring = None
            include = False
        if include:
            filepath = os.path.join(foldername, filename)
            print(filepath)
            image = cv2.imread(filepath)
            if moviewriter is None:
                height, width, channels = image.shape
                if width > 2000:
                    height = int(height / 2)
                    width = int(width / 2)
                moviewriter = cv2.VideoWriter(os.path.join(foldername, moviename), cv2.VideoWriter_fourcc(*'DIVX'), fps, (width, height))
            image = cv2.resize(image, (width, height))
            label = filename[0:4] + "-" + filename[4:6] + "-" + filename[6:8] + " " + filename[8:10] + ":" + filename[10:12] + ":" + filename[12:14]
            cv2.putText(image, label, (10, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 191, 0))

            moviewriter.write(image)

if moviewriter is not None:
    moviewriter.release()