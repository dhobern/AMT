#!/usr/bin/env python3
"""
AmtConfiguration - Class to encapsulate an AMT configuration file and associated metadata reporting

This class is used to handle modular settings for AMT components and to generate combined and 
extended versions as metadata output files.

Input files and output files are specified in YAML and organised around a number of named sections:

 - _configfiles - a list of YAML config files imported into the AmtConfiguration object

 - _errors - a list of error strings associated with constructing or managing the AmtConfiguration object
 
 - event - a dictionary of properties defining a Darwin Core event object
 
 - provenance - a dictionary containing a number of named subsections (dictionaries) each of which
    holds properties associated with a stage in generating or processing data. These subsections 
    allow all relevant metadata to be collected. Much of the metadata repurposes settings provided
    to AMT software modules. AmtConfiguration streamlines this process by using the same structures
    for settings and for metadata.

 - transfer - a dictionary providing instructions for file transfer

AmtConfiguration objects and output files serve different roles, as follows:

 - Input settings / output metadata for data collection and processing. In this case, the expected 
    elements will include:
     - _configfiles - list of input configuration files
     - _errors - list of errors encountered (may be absent)
     - event - elements that will ultimately form part of a data package e.g. to GBIF
     - provenance - a capture subsection documenting the hardware and the image capture settings, plus
        additional subsections for later stages in the processing pipeline (image segmentation, species
        identification, etc.)

 - Settings for controlling transfer of data over USB from AMT hardware and updating configuration and
    software in the AMT unit. In this case, the expected elements will include:
     - configfiles - list containing one entry - the name for the transfer settings YAML file
     - _errors - list of errors encountered (may be absent)
     - transfer - dictionary identifying transfer tasks to be executed
    
An AmtConfiguration instance is typically initialised with multiple YAML files, each of which supplies
a subset of the required elements (and may override values supplied by earlier YAML files). CONFIG_ALL 
includes an ordered list of filenames for this purpose. The filenames in this list are intended to 
represent the following components:

 - CONFIG_DEFAULTS - Standard default settings associated with the AMT software modules. These are 
    stored in YAML to avoid hardcoding the values in code. These values may be overwritten, normally
    via CONFIG_UNIT or CONFIG_SETTINGS.

 - CONFIG_UNIT - Settings that relate to the current hardware unit and that are unlikely to be
    altered between operations. This includes hardware options (GPIO pins, sensors, etc.) and a
    name for the unit (although this standardly defaults to the hostname).

 - CONFIG_SETTINGS - User-provided settings, including some event metadata, schedule settings, etc.
   These settings may be selected at runtime by providing an alternative file to use instead of 
   CONFIG_SETTINGS.

 - CONFIG_LOCATION - If a GPS sensor is enabled, it stores coordinates and GPS metadata in a
   separate YAML file, as part of the event section.

Usage:

 - AmtConfiguration(loadall = False, settingsfile = None) 
    Create configuration object and optionally initialise it with contents from existing 
    YAML configuration files. If loadAll is True, the configuration will be initialised 
    using a set of standardly named YAML files in a standard order (specified in CONFIG_ALL).
    If settingsFile is specified, this should identify a YAML configuration file which will
    either (if loadall is False) be loaded alone as the initial configuration or (if loadAll
    is True) replace the CONFIG_SETTINGS YAML file in CONFIG_ALL. In all cases, the 
    component YAML files are inserted using the add() method. Errors are logged inside
    the configuration object (as an _errors list). 

 - config.add(name, ignoreerrors = False)
    Add the contents of a YAML file to an existing AmtConfiguration object

 - config.set(key, value, section, subsection = None)
    Insert or update the value associated with a key in a named section and optional subsection

 - config.get(key, section, subsection = None)
    Get current value for specified key from named section and optional subsection

 - config.dump(filename = None)
    Write config as YAML to named file or to stdout

For more information on the autonomous moth trap project, see https://amt.hobern.net/.
"""
__author__ = "Donald Hobern"
__copyright__ = "Copyright 2021, Donald Hobern"
__credits__ = ["Donald Hobern"]
__license__ = "MIT"
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

# Identifier for event section (contains Darwin Core Event properties and other terms documenting the capture event)
SECTION_EVENT = "event"

"""
Darwin Core terms (see https://dwc.tdwg.org/terms/) and other contextual data properties relating to the capture event:
 - decimalLatitude, decimalLongitude, coordinateUncertaintyInMeters, geodeticDatum: See Darwin Core
 - coordinateTimestamp: Date and time at which coordinates were captured
 - sunsetTime: local ISO time for sunset preceding data capture or for next sunset if capture begins in daytime
 - sunriseTime: local ISO time for next sunrise
 - lunarPhase: current lunar phase as text string (one of 'New Moon, Waxing Crescent, First Quarter, Waxing Gibbous, Full Moon, Waning Gibbous, Last Quarter, Waning Crescent')
"""
EVENT_LATITUDE = "decimalLatitude"
EVENT_LONGITUDE = "decimalLongitude"
EVENT_COORDINATEUNCERTAINTY = "coordinateUncertaintyInMeters"
EVENT_GEODETICDATUM = "geodeticDatum"
EVENT_COORDINATETIMESTAMP = "coordinateTimestamp"
EVENT_SUNSETTIME = "sunsetTime"
EVENT_SUNRISETIME = "sunriseTime"
EVENT_LUNARPHASE = "lunarPhase"

# Identifier for provenance section (contains settings and metadata from all stages in processing)
SECTION_PROVENANCE = "provenance"

# Identifier for capture subsection of provenance section (contains settings and metadata for image capture)
SUBSECTION_CAPTURE = "capture"

"""
Properties relating to the capture of images (Section: provenance, Subsection: capture):
 - unitname: Unique identifier for the current AMT unit - should only include characters that can be used in a filename
 - mode: The operating model, currently only 'TimeLapse' is supported
 - processor: Document computer hardware details as part of metadata (e.g. 'Raspberry Pi Zero W')
 - camera: Document camera as part of metadata (e.g. 'Raspberry Pi HQ + 6mm Wide Angle Lens')
 - uvsource: Document attractant light details as part of metadata (e.g. 'High-power LED tube: 4 UV, 1 green, 1 blue')
 - illumination: Document image illumination details as part of metadata  (e.g. '10-inch ring light')
 - operatingdistance: Operating distance of the camera from the illuminated surface, in mm
 - imagewidth: Image width for camera resolution in pixels
 - imageheight: Image height for camera resolution in pixels
 - brightness: Image brightness for camera (0-100, PiCamera default is 50)
 - contrast: Image contrast for camera (-100-100, PiCamera default is 0)
 - saturation: Image saturation for camera (-100-100, PiCamera default is 0)
 - sharpness: Image sharpness for camera (-100-100, PiCamera default is 0)
 - quality: Image quality for camera (1-100, PiCamera default is 85)
 - awb_mode: Automated white balance setting for camera (one of 'off', 'auto', 'sunlight', 'cloudy', 'shade', 'tungsten', 'fluorescent', 'incandescent', 'flash', 'horizon', PiCamera default is 'auto')
 - awb_gains: Automated white balance red/blue gains for camera (a tuple with two float values for the red and blue gains)
 - envsensor: Installed temperature/humidity sensor (one of 'DHT22', 'DHT11', 'None')
 - gpssensor: Installed GPS sensor (e.g. 'BN220', 'None')
 - gpiogreen: Raspberry Pi GPIO pin for green side of red/green GPIO pin in BCM mode (default 25)
 - gpiored: Raspberry Pi GPIO pin for red side of red/green GPIO pin in BCM mode (default 7)
 - gpiolights: Raspberry Pi GPIO pin for activating lights in BCM mode (default 26)
 - gpioenvpower: Raspberry Pi GPIO pin for enabling 3.3V power to temperature/humidity sensor in BCM mode (default 10) - use -1 for power not from GPIO pin
 - gpioenvdata: Raspberry Pi GPIO pin for temperature/humidity sensor data in BCM mode (default 9)
 - gpiogpspower: Raspberry Pi GPIO pin for enabling 5.0V power to GPS sensor in BCM mode (default 24) - use -1 for power not from GPIO pin
 - gpiomanualmode: Raspberry Pi GPIO pin for indicating manual mode operation (default 22)
 - gpiotransfermode: Raspberry Pi GPIO pin for indicating transfer mode operation (default 27)
 - gpioshutdownmode: Raspberry Pi GPIO pin for indicating shutdown mode operation (default 17)
 - gpiomodetrigger: Raspberry Pi GPIO pin to receive signal to initiate modes (default 16)
 - folder: Destination folder for image sets - each run will create a subfolder containing a copy of the configuration file and all images
 - program: Image capture program executable
 - version: Image capture program version
 - trigger: Specify whether capture initiated manually or automatically, normally via crontab ('Manual' or 'Automatic')
 - statuslight: Specify whether to use red/green status light continually (true/false, defaults to false)
 - initialdelay: Delay in seconds between enabling lights and DHT22 sensor and starting to capture images
 - interval: Time lapse interval between images in seconds
 - maximages: Maximum number of images to collect (-1 for unlimited)
 - calibration: String containing a comma-delimited list (no spaces) of properties for collecting series of calibration images - any combination of quality, brightness, sharpness, contrast, saturation, awb_mode and awb_gains (default "")
"""
CAPTURE_UNITNAME = "unitname"
CAPTURE_MODE = "mode"
CAPTURE_PROCESSOR = "processor"
CAPTURE_CAMERA = "camera"
CAPTURE_UVSOURCE = "uvsource"
CAPTURE_ILLUMINATION = "illumination"
CAPTURE_OPERATINGDISTANCE = "operatingdistance"
CAPTURE_IMAGEWIDTH = "imagewidth"
CAPTURE_IMAGEHEIGHT = "imageheight"
CAPTURE_BRIGHTNESS = "brightness"
CAPTURE_CONTRAST = "contrast"
CAPTURE_SATURATION = "saturation"
CAPTURE_SHARPNESS = "sharpness"
CAPTURE_QUALITY = "quality"
CAPTURE_AWBMODE = "awb_mode"
CAPTURE_AWBGAINS = "awb_gains"
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

    """
    Initialise new AmtConfiguration with any specified YAML files, either the
    full suite of default configuration files with an option to override the
    amt_settings.yaml file with a user-specified file or else just a 
    user-specified file.

    loadall - Set to True to import all configuration files listed in
        CONFIG_ALL (silently in case any of these don't exist)
    settingfile - Filename for YAML configuration file to use in place
        of CONFIG_SETTINGS file or as only file to import
    """
    def __init__(self, loadall = False, settingsfile = None):
        self.data = {}
        if loadall:
            for file in CONFIG_ALL:
                ignoreerrors = False
                if settingsfile and file == CONFIG_SETTINGS:
                    file = settingsfile
                    ignoreerrors = True
                self.add(os.path.join(CONFIGURATION_FOLDER, file), ignoreerrors)
        elif settingsfile:
            self.add(os.path.join(CONFIGURATION_FOLDER, settingsfile))

    """
    Add a YAML configuration file, normally overwriting any existing values
    """
    def add(self, name, ignoreerrors = False):
        # Load YAML file and get data and errors
        data, errors = self.__loadconfig(name, ignoreerrors)

        # Log any errors in an _errors list inside the data
        if errors:
            self.__logerrors(errors)

        # Insert/update data with values from file
        if data:
            # Record name of file in _configfiles list in data
            if AmtConfiguration.FILES not in self.data:
                self.data[AmtConfiguration.FILES] = []    
            self.data[AmtConfiguration.FILES].append(name)

            # Use standard method to merge data from file
            self.data = self.__merge(self.data, data)

            return True

        return False

    """
    Set a keyed value in a dictionary named section and optionally
    in a subsection dictionary
    """
    def set(self, key, value, section, subsection = None):
        # Make sure section exists and is a dictionary
        if section not in self.data:
            self.data[section] = {}
        elif not isinstance(self.data[section], dict):
            logging.error('Section ' + section + ' exists but is not a dictionary')
            return False

        # Make sure any subsection exists and is a dictionary and 
        # set key-value in section or subsection as appropriate
        if subsection:
            if subsection not in self.data[section]:
                self.data[section][subsection] = {}
            elif not isinstance(self.data[section][subsection], dict):
                logging.error('Subsection ' + subsection + ' exists but is not a dictionary')
                return False
            self.data[section][subsection][key] = value
        else:
            self.data[section][key] = value
        
        return True
            
    """
    Get value by key from section or section/subsection - return None if not found
    """
    def get(self, key, section, subsection = None):
        # Does section dictionary exist?
        if section in self.data and isinstance(self.data[section], dict):
            # If subsection specified, see if it exists and get value for key
            if subsection:
                if subsection in self.data[section] and isinstance(self.data[section][subsection], dict) and key in self.data[section][subsection]:
                    return self.data[section][subsection][key]
            elif key in self.data[section]:
                return self.data[section][key]

        # Return None by default
        return None

    """
    Dump all content as YAML in block format either to stdout or to a file
    """
    def dump(self, filename = None):
        # If no filename specified, just print the data
        if not filename:
            print(yaml.dump(self.data, default_flow_style = False))
            return

        # Write YAML to the file
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
        # Loop through source keys
        for key in source:
            # Add values for missing keys (values may be lists or dictionaries)
            if key not in target:
                target[key] = source[key]

            # For existing keys:
            # - if the value is a dictionary, recursively merge
            # - if the value is a list, extend with all values
            # - in all other cases, replace with new value
            else:
                value = source[key]
                if isinstance(value, dict):
                    target[key] = self.__merge(target[key], value)
                elif isinstance(value, list):
                    target[key].extend(value)
                else:
                    target[key] = value

        # Return the target for easy chaining of calls
        return target

    """
    Create error list if not present and log errors
    """
    def __logerrors(self, errors):
        if errors is not None:
            if AmtConfiguration.ERRORS not in self.data:
                self.data[AmtConfiguration.ERRORS] = []
            self.data[AmtConfiguration.ERRORS].extend(errors)