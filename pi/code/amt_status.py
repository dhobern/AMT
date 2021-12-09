#!/usr/bin/env python
"""
amt_status - Utility to turn on/off or flash red/green status light

Syntax python red|green|off [flash count]

 - A colour selection, either red, green or off
 - An optional count for a number of on/off flashes (one second in selected colour and one second in colour when initialised)

The LED pins default to GPIO25 for green and GPIO7 for red (BCM mode) but may be overridden by amt_config.json.
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

color = 'off'
flashcount = 0

if len(sys.argv) > 1:
    color = sys.argv[1]

if len(sys.argv) > 2:
    flashcount = int(sys.argv[2])

initstatus(loadconfig())
showstatus(color, flashcount)