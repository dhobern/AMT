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

class AmtConfiguration():

    ERRORS = "_errors"
    FILES = "_configurationfiles"

    def __init__(self, baseconfigfile = "amt_defaultconfig.yaml"):
        self.data, errors = self.__loadconfig(baseconfigfile)
        if self.data is None:
            self.data = {}

        if AmtConfiguration.FILES not in self.data:
            self.data[AmtConfiguration.FILES] = [baseconfigfile]
        else:
            self.data[AmtConfiguration.FILES].extend(baseconfigfile)

        if errors is not None:
            self.__logerrors(errors)

    """
    Add a YAML configuration file, normally overwriting any existing values
    """
    def add(self, name):
        data, errors = self.__loadconfig(name)
        if errors is not None:
            self.__logerrors(errors)
        if data is not None:
            self.data[AmtConfiguration.FILES].append(name)
            self.data = self.__merge(self.data, data)
            return True
        return False

    """
    Dump all content in block format
    """
    def dump(self):
        print(yaml.dump(self.data, default_flow_style = False))

    """
    Load a YAML configuration file, returning data and errors
        - data: parsed YAML configuration file contents
        - errors: None or list of error strings
    """
    def __loadconfig(self, name):
        if not os.path.exists(name):
            return None, ["Configuration file not found: " + name]
        if not os.path.isfile(name):
            return None, ["Configuration file not a file: " + name]

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