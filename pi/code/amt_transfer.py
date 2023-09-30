#!/usr/bin/env python3
"""
amt_transfer - Transfer files to/from Autonomous Moth Trap

Performs a series of defined tasks relating to extracting images from trap or to updating 
configuration and scripts. Normally triggered by button push. Intended as tool for 
situations where wireless access to the trap is not possible or wished.

Configuration is provided via amt_transfer.yaml, with the following elements:

 - transferimages - true/false - If true, this script seeks to copy images and metadata for 
   all capture periods from the internal trap storage to a USB drive

 - deleteonexport - true/false - If true, this script deletes images and metadata from 
   the internal trap storage if and only if exportimages ran successfully to completion

 - deleteonetime - true/false - If true, this script deletes images and metadata from 
   the internal trap storage regardless of transfer success, and modifies 
   amt_transfer_yaml to set this value to false. This ensures that the user must select
   the delete option rather than repeating it in error. 

 - deleteall - true/false - If true, this script deletes images and metadata from 
   the internal trap storage regardless of transfer success. USE WITH CAUTION - unless
   manually changed, this setting will delete data. 

 - transfersettings - true/false - If true, this script 1) exports a backup copy of the 
   current version of amt_settings.yaml to a USB drive, and 2) imports a new amt_settings.yaml
   from the USB drive if one is present.

 - transfersoftware - true/false - If true, this script 1) exports a backup copy of all python 
   scripts to a USB drive, and 2) imports new versions from the USB drive if present. USE WITH
   CAUTION - if amt_modeselector.py or amt_transfer.py are among the scripts being replaced,
   errors may make the unit fail and prevent further software update by this route.

 The script checks /media/pi for subfolders (representing drives). If the subfolder 
 (i.e. the root folder of the drive) contains a folder named AMT itself containing a 
 file named amt_transfer.json, the script uses this as its configuration.

 The script logs progress in /media/usb/AMT/amt_transfer.log.

 If transferimages is specified, all folders and files from /home/pi/AMT/ are copied to
 /media/usb/AMT/captures/<UNITNAME>/.

 If transfersettings is specified, /home/pi/amt_settings.yaml is copied to
 /media/usb/AMT/backups/<UNITNAME>-<TIMESTAMP>/amt_config.json and /media/usb/AMT/amt_settings.yaml
 is copied to /home/pi/amt_settings.yaml.

 If transfersoftware is specified, python scripts named /home/pi/AMT/amt_*.py are copied to
 /media/usb/AMT/backups/<UNITNAME>-<TIMESTAMP>/ and scripts named /media/usb/AMT/amt_*.py
 are copied to /home/pi/.
"""
__author__ = "Donald Hobern"
__copyright__ = "Copyright 2021, Donald Hobern"
__credits__ = ["Donald Hobern"]
__license__ = "MIT"
__version__ = "0.9.0"
__maintainer__ = "Donald Hobern"
__email__ = "dhobern@gmail.com"
__status__ = "Production"

import time
from datetime import datetime
import subprocess
import os
import RPi.GPIO as GPIO
import sys
import socket
import json
import traceback
import logging

# Common utility functions
from amt_util import *

basefolder = "/media/usb"
capturetargetname = "captures"
unitname = "UNKNOWN"


# Check whether two folders already match in file contents
def filesmatch(folderA, folderB):
    if not os.path.isdir(folderA) or not os.path.isdir(folderB):
        return False

    filesA = os.listdir(folderA)
    filesB = os.listdir(folderB)

    for f in filesA:
        if f not in filesB:
            return False
        pathA = os.path.join(folderA, f)
        pathB = os.path.join(folderB, f)
        if os.path.isdir(pathA):
            if not os.path.isdir(pathB):
                return False
            if filesmatch(pathA, pathB):
                return False
        filesB.remove(f)

    if len(filesB) > 0:
        return False

    return True


def savefilebackup(folder, file):
    if os.path.isfile(file):
        backupsfolder = os.path.join(folder, "backups")
        if not os.path.isdir(backupsfolder):
            os.mkdir(backupsfolder)

        parts = file.split("/")
        newfile = os.path.join(backupsfolder, parts.pop())

        subprocess.call(["cp", file, newfile])
        logging.info("Copied " + file + " to " + newfile)


# Transfer files according to configured requirements
def transferfiles(config):
    configurationupdated = False

    # Check whether USB drive is attached

    unitname = config.get(CAPTURE_UNITNAME, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    if unitname is None:
        unitname = socket.gethostname()
    capturesource = config.get(CAPTURE_FOLDER, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    xferconfig = None

    amtfolder = os.path.join(basefolder, "AMT")
    if not os.path.exists(amtfolder):
        try:
            os.mkdir(amtfolder)
        except:
            logging.error("USB drive not present - cancelling transfer")
            return False

    timestamp = datetime.today().strftime("%Y%m%d-%H%M%S")
    timestampfolder = os.path.join(amtfolder, timestamp)
    if not os.path.exists(timestampfolder):
        os.mkdir(timestampfolder)

    loghandler = logging.FileHandler(os.path.join(timestampfolder, "amt_transfer.log"))
    formatter = logging.Formatter(
        unitname + ": %(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    loghandler.setFormatter(formatter)
    logging.getLogger().addHandler(loghandler)

    logging.info("AMT Transfer")

    xferconfigname = os.path.join(amtfolder, "amt_transfer.yaml")
    if os.path.exists(xferconfigname) and os.path.isfile(xferconfigname):
        xferconfig = AmtConfiguration(False, xferconfigname, False)
        logging.info("Loaded config file: " + xferconfigname)

    transferimages = False
    deleteontransfer = False
    deleteonetime = False
    deleteall = False
    transfersettings = False
    transfersoftware = False

    if xferconfig:
        transferimages = xferconfig.get(TRANSFER_IMAGES, SECTION_TRANSFER)
        deleteontransfer = xferconfig.get(TRANSFER_DELETEONTRANSFER, SECTION_TRANSFER)
        deleteonetime = xferconfig.get(TRANSFER_DELETEONETIME, SECTION_TRANSFER)
        deleteall = xferconfig.get(TRANSFER_DELETEALL, SECTION_TRANSFER)
        transfersettings = xferconfig.get(TRANSFER_SETTINGS, SECTION_TRANSFER)
        transfersoftware = xferconfig.get(TRANSFER_SOFTWARE, SECTION_TRANSFER)

    if deleteonetime:
        logging.info("deleteonetime is true - will delete all images")
        xferconfig.set(TRANSFER_DELETEONETIME, False, SECTION_TRANSFER)
        xferconfig.dump(xferconfigname)
        logging.info("deleteonetime reset to false in " + xferconfigname)

    if transferimages:
        logging.info("transferimage is true - exporting images")
        capturesfolder = os.path.join(amtfolder, capturetargetname)
        if not os.path.isdir(capturesfolder):
            os.mkdir(capturesfolder)
        capturedestination = os.path.join(capturesfolder, unitname)
        if not os.path.isdir(capturedestination):
            os.mkdir(capturedestination)
        success = True
        logging.info("Copying from " + capturesource + " to " + capturedestination)
        if os.path.isdir(capturesource):
            for c in os.listdir(capturesource):
                try:
                    capturesubfolder = os.path.join(capturesource, c)
                    destinationsubfolder = os.path.join(capturedestination, c)
                    # Don't copy files that have already been copied
                    if not filesmatch(capturesubfolder, destinationsubfolder):
                        subprocess.call(
                            ["cp", "-fr", capturesubfolder, capturedestination],
                            shell=False,
                        )
                        logging.info("Copied " + capturesubfolder)
                    else:
                        logging.info(
                            "Folder already copied: " + capturesubfolder + " - skipping"
                        )
                except:
                    logging.exception("Error copying files")
                    success = False
                    logging.error("Copy of " + capturesubfolder + " failed")

            if deleteall:
                logging.info("deleteall is true - deleting all images")
            elif deleteonetime:
                logging.info("deleteonetime is true - deleting all images")
                deleteall = True
            elif deleteontransfer:
                if success:
                    logging.info(
                        "deleteontransfer is true and transfer succeeded - deleting all images"
                    )
                    deleteall = True
                else:
                    logging.info(
                        "deleteontransfer is true but transfer failed - skipping deletion"
                    )

            if deleteall:
                logging.info("Deleting from " + capturesource)
                for c in os.listdir(capturesource):
                    try:
                        capturesubfolder = os.path.join(capturesource, c)
                        subprocess.call(["rm", "-fr", capturesubfolder], shell=False)
                        logging.info("Deleted " + capturesubfolder)
                    except Error as err:
                        logging.error("Error removing files " + str(err.args[0]))
                        break

    if transfersettings:
        logging.info("transferimage is true - importing configuration files")

        # Transfer any files named amt_settings.yaml or amt_settings.xxx.yaml. The first
        # of these is the default for overriding settings. Any other settings files with
        # modifiers in their names can be used to vary behaviour between automated (i.e.
        # crontab) runs.
        for f in os.listdir(amtfolder):
            if f.startswith("amt_settings.") and f.endswith(".yaml"):
                logging.info("Importing " + f)
                importconfigurationfile = os.path.join(amtfolder, f)
                localconfigurationfile = os.path.join("/home/pi", f)

                savefilebackup(timestampfolder, localconfigurationfile)
                subprocess.call(["cp", importconfigurationfile, localconfigurationfile])

                configurationupdated = True

        if configurationupdated:
            logging.info("Configuration updated")
        else:
            logging.error("No configuration files found in " + amtfolder)

    if transfersoftware:
        logging.info("transferimage is true - updating software")

        for f in os.listdir(amtfolder):
            if (
                f.startswith("amt_")
                and f.endswith(".py")
                and f not in ["amt_transfer.py", "amt_modeselector.py"]
            ):
                pythonfile = os.path.join("/home/pi", f)
                newpythonfile = os.path.join(amtfolder, f)
                savefilebackup(timestampfolder, pythonfile)
                subprocess.call(["cp", newpythonfile, pythonfile])
                logging.info("Software updated - " + f)

    logging.info("Copying logfiles")
    for f in os.listdir("/home/pi"):
        if f.startswith("amt_") and f.endswith(".log"):
            logfile = os.path.join("/home/pi", f)
            savefilebackup(timestampfolder, logfile)
            if f != "amt_modeselector.log":
                os.remove(logfile)

    logging.getLogger().removeHandler(loghandler)

    return configurationupdated


# Run main
if __name__ == "__main__":
    initlog("/home/pi/amt_transfer.log")
    config = AmtConfiguration(True)
    transferfiles(config)

    try:
        subprocess.call(["sudo", "umount", "--force", "/media/usb"], shell=False)
    except Error:
        logging.exception("Could not unmount drive")
