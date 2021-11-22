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
 /media/pi/<DRIVENAME>/AMT/captures/<UNITNAME>/.

 If importconfiguration is specified, the current configuration file is copies to
 /media/pi/<DRIVENAME>/AMT/backups/<UNITNAME>-<TIMESTAMP>/amt_config.json
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
from shutil import copyfile, copytree, rmtree, Error
import os
import RPi.GPIO as GPIO
import sys
import json
import traceback
import logging

# Common utility functions
from amt_util import *

basefolder = '/media/usb'
capturesource = '/home/pi/AMT'
capturetargetname = 'captures'
unitname = "UNKNOWN"

# Transfer files according to configured requirements
def transferfiles():
    mainconfig = loadconfig()
    if mainconfig is not None:
        if "unitname" in mainconfig:
            unitname = mainconfig['unitname']
        if "folder" in mainconfig:
            capturesource = mainconfig['folder']
    xferconfig = None
    amtfolder = os.path.join(basefolder, "AMT")
    if os.path.isdir(amtfolder):
        xferconfigname = os.path.join(amtfolder, "amt_transfer.json")
        if os.path.isfile(xferconfigname):
            xferconfig = loadconfig(xferconfigname)
            print("Loaded config file")
            print(str(xferconfig))

    if xferconfig is None:
        print("No config file")
        return(1)

    if 'exportimages' in xferconfig and xferconfig['exportimages']:
        print("Exporting images")
        capturesfolder = os.path.join(amtfolder, capturetargetname)
        if not os.path.isdir(capturesfolder):
            os.mkdir(capturesfolder)
        capturedestination = os.path.join(capturesfolder, unitname)
        if not os.path.isdir(capturedestination):
            os.mkdir(capturedestination)
        success = True
        print("Copying from " + capturesource + " to " + capturedestination)
        if os.path.isdir(capturesource):
            for c in os.listdir(capturesource):
                try:
                    capturesubfolder = os.path.join(capturesource, c)
                    destinationsubfolder = os.path.join(capturedestination, c)
                    copytree(capturesubfolder, destinationsubfolder)
                except Error as err:
                    #errors.extend(err.args[0])
                    print("Error copying files " + str(err.args[0]))
                    success = False
                    print("Copy of " + capturesubfolder + " failed")
                print("Copied " + capturesubfolder)
            if success and 'deleteonexport' in xferconfig and xferconfig['deleteonexport']:
                for c in os.listdir(capturesource):
                    try:
                        capturesubfolder = os.path.join(capturesource, c)
                        rmtree(capturesubfolder)
                    except Error as err:
                        #errors.extend(err.args[0])
                        print("Error removing files " + str(err.args[0]))
                        break


# Run main
if __name__=="__main__": 
   transferfiles()