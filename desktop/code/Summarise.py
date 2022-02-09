#!/usr/bin/env python
"""
Summarise.py - Generate summary overview of AMT trap runs
"""
__author__ = "Donald Hobern"
__copyright__ = "Copyright 2021, Donald Hobern"
__credits__ = ["Donald Hobern"]
__license__ = "CC-BY-4.0"
__version__ = "1.0.0"
__maintainer__ = "Donald Hobern"
__email__ = "dhobern@gmail.com"
__status__ = "Production"

import os
import sys
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

if len(sys.argv) >= 2:
    config_filename = sys.argv[1]
else:
    config_filename = "../config/AMT_config_zero.json"

conf = readconfig(config_filename)
basefolder = conf['datapath']

for f in os.listdir(basefolder):
    lat, lon, unc, lun, ris, set = None, None, None, None, None, None
    metadatafile = os.path.join(basefolder, f, 'amt_metadata.yaml')
    if os.path.isfile(metadatafile):
        with open(metadatafile, newline='') as metadata:
            for line in metadata:
                terms = line.strip().split(':')
                if len(terms) > 1:
                    key = terms[0].strip()
                    if key == 'decimalLatitude': 
                        lat = float(terms[1].strip())
                    elif key == 'decimalLongitude': 
                        lon = float(terms[1].strip())
                    elif key == 'coordinateUncertaintyInMeters': 
                        unc = float(terms[1].strip())
                    elif key == 'lunarPhase': 
                        lun = terms[1].strip()
                    elif key == 'sunsetTime': 
                        set = ':'.join(terms[1:]).strip().strip("'")
                    elif key == 'sunriseTime': 
                        ris = ':'.join(terms[1:]).strip().strip("'")
    print(f + ": " + str(lon) + ", " + str(lat) + ", " + str(unc) + ", " + str(lun) + ", " + str(set) + ", " + str(ris))
