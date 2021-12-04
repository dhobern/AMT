#!/usr/bin/env python3
"""
amt_config - Class to encapsulate an AMT configuration file and associated metadata reporting

 - loadconfig(filename = "amt_config.json") - load amt_config.json or specified JSON config files - returns config data as dictionary
 - selectpin(config, key, default, nullable = False) - return GPIO pin in BCM mode based on config file - returns pin number
 - initstatus(config) - set up status light based on config file - returns current state of light
 - showstatus(color, flashcount = 0) - set status light color or flash status light a number of times
 - converttz(time, from_zone, to_zone) - map datetime to specified timezone, returns modified datetime object
 - getsuntimes(latitude, longitude) - get sunrise and sunset for coming/present night from coordinates, returns two datetimes for sunset and sunrise, respectively
 - getlunarphase() - get current lunar phase as string, returns one of "New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous", "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent"

For more information see https://amt.hobern.net/.
"""
__author__ = "Donald Hobern"
__copyright__ = "Copyright 2021, Donald Hobern"
__credits__ = ["Donald Hobern"]
__license__ = "CC-BY-4.0"
__version__ = "0.9.0"
__maintainer__ = "Donald Hobern"
__email__ = "dhobern@gmail.com"
__status__ = "Production"

import yaml
import os
import logging

CONFIGURATION_FOLDER = "/home/pi"

CONFIG_DEFAULTS = "amt_defaults.yaml"
CONFIG_UNIT = "amt_unit.yaml"
CONFIG_SETTINGS = "amt_settings.yaml"
CONFIG_LOCATION = "amt_location.yaml"

CONFIG_ALL = [ CONFIG_DEFAULTS, CONFIG_UNIT, CONFIG_SETTINGS, CONFIG_LOCATION ]

CONFIG_METADATA = "amt_metadata.yaml"

SECTION_EVENT = "event"
EVENT_LATITUDE = "decimalLatitude"
EVENT_LONGITUDE = "decimalLongitude"
EVENT_COORDINATEUNCERTAINTY = "coordinateUncertaintyInMeters"
EVENT_COORDINATETIMESTAMP = "coordinateTimestamp"
EVENT_GEODETICDATUM = "geodeticDatum"
EVENT_SUNSETTIME = "sunsetTime"
EVENT_SUNRISETIME = "sunriseTime"
EVENT_LUNARPHASE = "lunarPhase"

SECTION_PROVENANCE = "provenance"
SUBSECTION_CAPTURE = "capture"
CAPTURE_UNITNAME = "unitname"
CAPTURE_MODE = "mode"
CAPTURE_PROCESSOR = "processor"
CAPTURE_CAMERA = "camera"
CAPTURE_OPERATINGDISTANCE = "operatingdistance"
CAPTURE_UVSOURCE = "uvsource"
CAPTURE_ILLUMINATION = "illumination"
CAPTURE_ENVSENSOR = "envsensor"
CAPTURE_GPSSENSOR = "gpssensor"
CAPTURE_GPIOGREEN = "gpiogreen"
CAPTURE_GPIORED = "gpiored"
CAPTURE_GPIOLIGHTS = "gpiolights"
CAPTURE_GPIOENVPOWER = "gpioenvpower"
CAPTURE_GPIOENVDATA = "gpioenvdata"
CAPTURE_GPIOGPSPOWER = "gpiogpspower"
CAPTURE_GPIOMANUALMODE = "gpiomanualmode"
CAPTURE_GPIOTRANSFERMODE = "gpiotransfermode"
CAPTURE_GPIOSHUTDOWNMODE = "gpioshutdownmode"
CAPTURE_GPIOMODETRIGGER = "gpiomodetrigger"
CAPTURE_FOLDER = "folder"
CAPTURE_IMAGEWIDTH = "imagewidth"
CAPTURE_IMAGEHEIGHT = "imageheight"
CAPTURE_BRIGHTNESS = "brightness"
CAPTURE_CONTRAST = "contrast"
CAPTURE_SATURATION = "saturation"
CAPTURE_SHARPNESS = "sharpness"
CAPTURE_QUALITY = "quality"
CAPTURE_AWBMODE = "awb_mode"
CAPTURE_AWBGAINS = "awb_gains"
CAPTURE_PROGRAM = "program"
CAPTURE_VERSION = "version"
CAPTURE_TRIGGER = "trigger"
CAPTURE_STATUSLIGHT = "statuslight"
CAPTURE_INITIALDELAY = "initialdelay"
CAPTURE_INTERVAL = "interval"
CAPTURE_MAXIMAGES = "maximages"
CAPTURE_CALIBRATION = "calibration"

SECTION_TRANSFER = "transfer"
TRANSFER_IMAGES = "transferimages"
TRANSFER_DELETEONTRANSFER = "deleteontransfer"
TRANSFER_DELETEONETIME = "deleteonetime"
TRANSFER_DELETEALL = "deleteall"
TRANSFER_SETTINGS = "transfersettings"

class AmtConfiguration():

    ERRORS = "_errors"
    FILES = "_configurationfiles"

    def __init__(self, loadAll = False, settingsfile = None):
        self.data = {}
        if loadAll:
            for file in CONFIG_ALL:
                ignoreerrors = False
                if file == CONFIG_SETTINGS and settingsfile is not None:
                    file = settingsfile
                    ignoreerrors = True
                self.add(os.path.join(CONFIGURATION_FOLDER, file), ignoreerrors)
        elif settingsfile is not None:
            self.add(os.path.join(CONFIGURATION_FOLDER, settingsfile))

    def set(self, key, value, section, subsection = None):
        if section not in self.data:
            self.data[section] = {}
        elif not isinstance(self.data[section], dict):
            logging.error('Section ' + section + ' exists but is not a dictionary')
            return False

        if subsection is not None:
            if subsection not in self.data[section]:
                self.data[section][subsection] = {}
            elif not isinstance(self.data[section][subsection], dict):
                logging.error('Subsection ' + subsection + ' exists but is not a dictionary')
                return False
            self.data[section][subsection][key] = value
        else:
            self.data[section][key] = value
        
        return True
            
    def get(self, key, section, subsection = None):
        if section in self.data and isinstance(self.data[section], dict):
            if subsection is not None:
                if subsection in self.data[section] and isinstance(self.data[section][subsection], dict) and key in self.data[section][subsection]:
                    return self.data[section][subsection][key]
            elif key in self.data[section]:
                return self.data[section][key]
        return None

    """
    Add a YAML configuration file, normally overwriting any existing values
    """
    def add(self, name, ignoreerrors = False):
        data, errors = self.__loadconfig(name, ignoreerrors)
        if errors is not None:
            self.__logerrors(errors)
        if data is not None:
            if AmtConfiguration.FILES not in self.data:
                self.data[AmtConfiguration.FILES] = []    
            self.data[AmtConfiguration.FILES].append(name)
            self.data = self.__merge(self.data, data)
            return True
        return False

    """
    Dump all content in block format
    """
    def dump(self, filename = None):
        if filename is None:
            print(yaml.dump(self.data, default_flow_style = False))
            return

        with open(filename, 'w', newline='', encoding='utf8') as file:
            yaml.dump(self.data, file, default_flow_style = False)

    """
    Load a YAML configuration file, returning data and errors
        - data: parsed YAML configuration file contents
        - errors: None or list of error strings
    """
    def __loadconfig(self, name, ignoreerrors = False):
        if not os.path.exists(name):
            if not ignoreerrors:
                return None, ["Configuration file not found: " + name]
            else:
                return None, None
        if not os.path.isfile(name):
            if not ignoreerrors:
                return None, ["Configuration file not a file: " + name]
            else:
                return None, None

        data = None
        errors = None
        with open(name, "r") as stream:
            try:
                data = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                errors = [ str(exc) ]

        return data, errors

    """
    Merge source dictionary into target dictionary
    """
    def __merge(self, target, source):
        for key in source:
            if key not in target:
                target[key] = source[key]
            else:
                value = source[key]
                if isinstance(value, dict):
                    target[key] = self.__merge(target[key], value)
                elif isinstance(value, list):
                    target[key].extend(value)
                else:
                    target[key] = value
        return target

    """
    Create error list if not present and log errors
    """
    def __logerrors(self, errors):
        if errors is not None:
            if AmtConfiguration.ERRORS not in self.data:
                self.data[AmtConfiguration.ERRORS] = []
            self.data[AmtConfiguration.ERRORS].extend(errors)