#!/usr/bin/env python3

from datetime import datetime, timedelta
from suntime import Sun, SunTimeException
from dateutil import tz
import math, decimal

# Convert datetime between timezones
def converttz(time, from_zone, to_zone):
    time = time.replace(tzinfo=from_zone)
    return time.astimezone(to_zone)

# Return sunset and sunrise times in local timezone
#
# Normally, this function is called after sunset (i.e. when the trap is running), but it
# may be called before sunset (if the trap starts during daylight hours).
# 
# The key question is when the NEXT sunrise will occur. (If the trap runs and ends 
# before sunset, this case can still be measured in relation to the coming night (as a 
# negative offset).
#
# The function therefore gets sunrise for the current date. If this time is prior to the 
# current time, the function requests the sunrise time for the subsequent day. Ragardless,
# it then requests the sunset time for the day before the sunrise time.
#
# Returns sunsettime, sunrisetime
def getsuntimes(latitude, longitude):
    sun = Sun(latitude, longitude)
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    now = datetime.today().replace(tzinfo=to_zone)
    sunrise = converttz(sun.get_sunrise_time(), from_zone, to_zone)

    if now > sunrise:
        sunrise = converttz(sun.get_sunrise_time(now + timedelta(days=1)), from_zone, to_zone)

    sunset = converttz(sun.get_sunset_time(sunrise - timedelta(days=1)), from_zone, to_zone)

    return sunset, sunrise

# Return lunar phase
# Author: Sean B. Palmer, inamidst.com
# Cf. http://en.wikipedia.org/wiki/Lunar_phase#Lunar_phase_calculation
def getlunarphase():
    dec = decimal.Decimal
    now = datetime.now()

    diff = now - datetime(2001, 1, 1)
    days = dec(diff.days) + (dec(diff.seconds) / dec(86400))
    pos = dec("0.20439731") + (days * dec("0.03386319269")) % dec(1)
    index = (pos * dec(8)) + dec("0.5")
    index = math.floor(index)
    return {
        0: "New Moon", 
        1: "Waxing Crescent", 
        2: "First Quarter", 
        3: "Waxing Gibbous", 
        4: "Full Moon", 
        5: "Waning Gibbous", 
        6: "Last Quarter", 
        7: "Waning Crescent"
    }[int(index) & 7]

def main():
    sunset, sunrise = getsuntimes(-35.264, 149.084)
    print("Sunset: " + sunset.strftime('%Y%m%d-%H%M%S') + " Sunrise: " + sunrise.strftime('%Y%m%d-%H%M%S') + " Moon: " + getlunarphase())

# Run main
if __name__=="__main__": 
   main()