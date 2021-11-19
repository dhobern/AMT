#!/usr/bin/env python3
"""
amt_transfer - Transfer files to/from Autonomous Moth Trap

Performs a series of defined tasks relating to extracting images from trap or to updating 
configuration and scripts. Normally triggered by button push. Intended as tool for 
situations where wireless access to the trap is not possible or wished.

Configuration is provided via amt_transfer.json, with the following elements:

 - exportimages - true/false - If true, this script seeks to copy images and metadata for 
   all capture periods from the internal trap storage to a USB drive

 - deleteonexport - true/false - If true, this script deletes images and metadata from 
   the internal trap storage if and only if exportimages ran successfully to completion

 - importconfiguration - true/false - If true, this script 1) exports a copy of the 
   current configuration file to a USB drive, and 2) imports a new configuration file 
   from the USB drive

 The script checks /media/pi for subfolders (representing drives). If the subfolder 
 (i.e. the root folder of the drive) contains a folder named AMT itself containing a 
 file named amt_transfer.json, the script uses this as its configuration.

 The script logs progress in /media/pi/<DRIVENAME>/AMT/amt_transfer.log.

 If exportimages is specified, all folders and files from /home/pi/AMT/ are copied to
 /media/pi/<DRIVENAME>/AMT/captures/.

 If importconfiguration is specified, the current configuration file is copies to
 /media/pi/<DRIVENAME>/AMT/backups/<TIMESTAMP>/amt_config.json
"""
__author__ = "Donald Hobern"
__copyright__ = "Copyright 2021, Donald Hobern"
__credits__ = ["Donald Hobern"]
__license__ = "CC-BY-4.0"
__version__ = "0.9.0"
__maintainer__ = "Donald Hobern"
__email__ = "dhobern@gmail.com"
__status__ = "Production"

import time
from datetime import datetime
from shutil import copyfile, copytree
import os
import RPi.GPIO as GPIO
import sys
import json
import logging

# Common utility functions
from amt_util import *

basefolder = '/media/pi'
capturefolder = '/home/pi/AMT'
capturetargetname = 'captures'

# Main body - initialise, run and clean up
def main():
    xfercxferconfig = None
    for f in os.listdir(basefolder):
        amtfolder = os.path.join(basefolder, f, "AMT")
        if os.path.isdir(amtfolder):
            xferconfigname = os.path.join(amtfolder, "amt_transfer.json")
            if os.path.isfile(xferconfigname):
                xferconfig = loadconfig(xferconfig)
                break

    if xferconfig is None:
        exit(0)

    if exportimages in xferconfig and xferconfig['expertimages']:
        capturedestination = os.path.join(amtfolder, capturetargetname)
        if not os.path.isdir(capturedestination):
            os.mkdir(capturedestination)
        success = True
        if os.path.isdir(capturefolder):
            for c in os.listdir(capturefolder):
                try:
                    capturesubfolder = os.path.join(capturefolder, c)
                    shutil.copytree(capturesubfolder, capturedestination)
                except:
                    success = False
                    print("Copy of " + capturesubfolder + " failed")
            if success and 'deleteonexport' in xferconfig and xfercxferconfig['deleteonexport']:
                for c in os.listdir(capturefolder):
                    try:
                        capturesubfolder = os.path.join(capturefolder, c)
                        shutil.tree(capturesubfolder)
                    except:
                        success = False
                        print("Removal of " + capturesubfolder + " failed")
                        break


# Run main
if __name__=="__main__": 
   main()