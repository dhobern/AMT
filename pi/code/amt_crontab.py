#!/usr/bin/env python
"""
amt_crontab - Utility to set crontab based on sunrise and sunset

Syntax python amt_crontab

"""
__author__ = "Donald Hobern"
__copyright__ = "Copyright 2021, Donald Hobern"
__credits__ = ["Donald Hobern"]
__license__ = "MIT"
__version__ = "0.9.1"
__maintainer__ = "Donald Hobern"
__email__ = "dhobern@gmail.com"
__status__ = "Production"

import sys
import time
from amt_util import *
from crontab import CronTab
from datetime import datetime, timedelta

def usage(exitafterdisplay, message = None):
    if message is not None:
        print("\namt_crontab.py message: " + message + "\n")
    print("Usage: python amt_crontab.py startpoint endpoint [maxminutes]")
    print("\n       startpoint - nightoffset - time to begin automated capture")
    print("       endpoint - nightoffset - time to end automated capture")
    print("       startpoint - int - maximum number of minutes for automated capture period (optional)")
    print("\n       where nightoffset is one of the following:")
    print("              sunset[+/-minutes] (e.g. \"sunset\", \"sunset+60\", \"sunset-30\")")
    print("              sunrise[+/-minutes] (e.g. \"sunrise\", \"sunrise-180\")")
    print("              middle[+/-minutes] (e.g. \"middle\", \"middle-120\")")
    if exitafterdisplay:
        sys.exit(0)

def getpoint(arg, ss, sr, mn):
    if arg.startswith("sunset"):
        base = ss
        offset = arg[6:]
    elif arg.startswith("sunrise"):
        base = sr
        offset = arg[7:]
    elif arg.startswith("middle"):
        base = mn
        offset = arg[6:]
    else:
        usage(True)

    if len(offset) > 0:
        return base + timedelta(minutes=int(offset))

    return base

def schedulejob(job, dt, offset = 0):
    actual = dt + timedelta(minutes=offset)
    job.minute.on(actual.minute)
    job.hour.on(actual.hour)

latitude = -35.264047
longitude = 149.083427

sunset, sunrise = getsuntimes(None, latitude, longitude)
middle = sunset + (sunrise - sunset) / 2

print ("Sunset " + str(sunset) + " Sunrise " + str(sunrise) + " Midpoint " + str(middle))

if len(sys.argv) < 3:
    usage(True)

startpoint = getpoint(sys.argv[1], sunset, sunrise, middle)
endpoint = getpoint(sys.argv[2], sunset, sunrise, middle)
if len(sys.argv) > 3:
    maxminutes = int(sys.argv[3])
    if (endpoint - startpoint).total_seconds() / 60 > maxminutes:
        endpoint = startpoint + timedelta(minutes=maxminutes)

if startpoint >= endpoint:
    usage(True, "Start time " + str(startpoint) + " must be before end time " + str(endpoint))

cron = CronTab(user=True)
for job in cron:
    if "lighton.py" in job.command:
        schedulejob(job, startpoint, -1)
    elif job.command == "motion":
        schedulejob(job, startpoint)
    elif "setCamera" in job.command:
        schedulejob(job, startpoint, 1)
    elif job.command == "pkill motion":
        schedulejob(job, endpoint)
    elif "lightoff.py" in job.command:
        schedulejob(job, endpoint, 1)
    elif "backup.sh" in job.command:
        schedulejob(job, endpoint, 2)

cron.write()

