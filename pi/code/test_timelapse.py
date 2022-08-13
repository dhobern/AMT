#!/usr/bin/env python3
__author__ = "Donald Hobern"
__copyright__ = "Copyright 2021, Donald Hobern"
__credits__ = ["Donald Hobern"]
__license__ = "MIT"
__version__ = "0.9.2"
__maintainer__ = "Donald Hobern"
__email__ = "dhobern@gmail.com"
__status__ = "Production"

from amt_config import *
from amt_util import *
from picamera import PiCamera
from datetime import datetime
from shutil import copyfile

# Return camera initialised using properties from config file - note that camera is already in preview when returned
def initcamera(config):
    camera = PiCamera()
    camera.resolution = (config.get(CAPTURE_IMAGEWIDTH, SECTION_PROVENANCE, SUBSECTION_CAPTURE), config.get(CAPTURE_IMAGEHEIGHT, SECTION_PROVENANCE, SUBSECTION_CAPTURE))
    brightness = config.get(CAPTURE_BRIGHTNESS, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    if brightness is not None:
        camera.brightness = brightness
    contrast = config.get(CAPTURE_CONTRAST, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    if contrast is not None:
        camera.contrast = contrast
    saturation = config.get(CAPTURE_SATURATION, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    if saturation is not None:
        camera.saturation = saturation
    sharpness = config.get(CAPTURE_SHARPNESS, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    if sharpness is not None:
        camera.sharpness = sharpness
    awb_mode = config.get(CAPTURE_AWBMODE, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    if awb_mode is not None:
        camera.awb_mode = awb_mode
    meter_mode = config.get(CAPTURE_METERMODE, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    if meter_mode is not None:
        camera.meter_mode = meter_mode
    awb_gains = config.get(CAPTURE_AWBGAINS, SECTION_PROVENANCE, SUBSECTION_CAPTURE)
    if awb_gains is not None and isinstance(awb_gains, list) and len(awb_gains) == 2:
        camera.awb_gains = awb_gains
    camera.start_preview()
    print("Camera initialised")
    return camera

# Main body - initialise, run and clean up
def timelapse(manuallytriggered = False):
    # Initialise from config settings
    config = AmtConfiguration(True, "amt_settings.yaml")
    index = 0
    while index < 100:
        try:
            # Capture image with metadata in filename
            camera = initcamera(config)

            imagetimestamp = datetime.today()
            index += 1
            imagename = "test_" + imagetimestamp.strftime('%Y%m%d%H%M%S') + "_" + str(index) + '.jpg'
            print("Capturing image " + imagename)
            camera.capture(imagename, format = "jpeg")
            print("Captured image " + imagename)

            camera.close()
        except:
            logging.exception("Caught exception in main loop")

# Run main
if __name__=="__main__":
   timelapse()
