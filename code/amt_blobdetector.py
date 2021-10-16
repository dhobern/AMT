import cv2
import os
import math
import numpy as np
from colors import reportcolors
from skimage import io

#Reference simple - https://docs.opencv.org/3.4/d7/d4d/tutorial_py_thresholding.html
# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_video/py_bg_subtraction/py_bg_subtraction.html
#Modified by Donald Hobern from CustomBlobDetector 19 September 2021

IDENTICAL = 1
RECT1_IN_RECT2 = 2
RECT2_IN_RECT1 = 3
OVERLAP = 4
DISJUNCT = 5

class AMTBlobDetector:
    def __init__(self, config):
        self.config = config['blobdetector']
        self.background = None
        self.kernel_fast = self.config["kernel"]
        self.thresh = self.config["thresh"]
        self.minarea = self.config["minarea"]
        self.maxarea = self.config["maxarea"]
        self.frame_id = 1
        self.bsmog2_bgnd = cv2.createBackgroundSubtractorMOG2()
        self.bsmog2_prev = cv2.createBackgroundSubtractorMOG2()

    def initialisebackground(self, image):
        background = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        height, width, channels = image.shape
        kernel = np.ones((5,5),np.float32)/25
        background = cv2.filter2D(background,-1,kernel)
        flipped = cv2.flip(background, 0)
        mask = cv2.compare(background, flipped, cv2.CMP_LT)
        background[np.where(mask == 255)] = flipped[np.where(mask == 255)]
        flipped = cv2.flip(background, 1)
        mask = cv2.compare(background, flipped, cv2.CMP_LT)
        background[np.where(mask == 255)] = flipped[np.where(mask == 255)]
        background = cv2.filter2D(background,-1,kernel)
        return background

    def getillumination(self, x, y):
        if self.background is None:
            return 0
        return int(self.background[y, x])

    def getrects(self, image, bsmog2, rate):
        image = bsmog2.apply(image, learningRate = rate)
        image[image > self.thresh] = 254
        image[image <= self.thresh] = 1
        image[image == 254] = 0
        image[image == 1] = 255
        kernel = np.ones((self.kernel_fast, self.kernel_fast), np.uint8)
        image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
        image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
        binary = image.copy()
        contours, _= cv2.findContours(255 - binary.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        rects = []
        for cnt in contours:
            rect = cv2.boundingRect(cnt)
            rectsize = rect[2] * rect[3]
            if rectsize > self.minarea and rectsize < self.maxarea:
                rects.append(rect)
        return binary, rects

    def comparerects(self, rect1, rect2):
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2
        if x1 >= x2 + w2 or x2 >= x1 + w1 or y1 > y2 + h2 or y2 > y1 + h2:
            return DISJUNCT
        if x1 == x2 and y1 == y2 and w1 == w2 and h1 == h2:
            return IDENTICAL
        if x1 >= x2 and x1 + w1 <= x2 + w2 and y1 >= y2 and y1 + h1 <= y2 + h2:
            return RECT2_IN_RECT1
        if x1 <= x2 and x1 + w1 >= x2 + w2 and y1 <= y2 and y1 + h1 >= y2 + h2:
            return RECT1_IN_RECT2
        return OVERLAP

    def drawrect(self, image, rect, color, linewidth = 2):
        x, y, w, h = rect
        cv2.rectangle(image, (x, y), (x + w, y + h), color, linewidth)
        return        

    def checkintersection(self, x1, y1, w1, h1, rectset):
        for r in rectset:
            x2, y2, w2, h2 = r
            if not (x1 >= x2 + w2 or x2 >= x1 + w1 or y1 >= y2 + h2 or y2 >= y1 + h1):
                return True
        return False

    def mostlyincluded(self, r1, r2):
        l1, t1, w1, h1 = r1
        r1 = l1 + w1
        b1 = t1 + h1
        x1 = (l1 + r1) / 2
        y1 = (t1 + b1) / 2
        l2, t2, w2, h2 = r2
        r2 = l2 + w2
        b2 = t2 + h2
        x2 = (l2 + r2) / 2
        y2 = (t2 + b2) / 2

        if x1 < l2 or x1 > r2 or y1 < t2 or y1 > b2:
            return False
        
        l = l1 if l1 > l2 else l2
        r = r1 if r1 < r2 else r2
        t = t1 if t1 > t2 else t2
        b = b1 if b1 < b2 else b2

        a = (r - l) * (b - t)

        if a / (w1 * h1) > 0.8:
            return True

        return False
        

    def findblobs(self, img, imageid):
        if self.background is None:
            self.background = self.initialisebackground(img)
            self.bsmog2_bgnd.apply(self.background)
            self.bsmog2_prev.apply(self.background)
        original = img.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        binary, rects_bgnd = self.getrects(gray, self.bsmog2_bgnd, 0)
        _, rects_prev = self.getrects(gray, self.bsmog2_prev, -1)

        blobs = []

        # Init counters for counting number of images
        count = 0

        iheight, iwidth, _ = img.shape

        for r in rects_bgnd:
            x, y, w, h = r
            blob = {}
            blob["imageid"] = imageid

            blob["x"], blob["y"], blob["w"], blob["h"] = x, y, w, h
            blob["xcenter"] = int(x + w / 2)
            blob["ycenter"] = int(y + h / 2)

            xcrop = math.floor(x - w * 0.5)
            wcrop = w + math.ceil(2 * w * 0.5)
            ycrop = math.ceil(y - h * 0.5)
            hcrop = h + math.ceil(2 * h * 0.5)
            if xcrop < 0:
                xcrop = 0
            if xcrop + wcrop > iwidth:
                wcrop = iwidth - xcrop
            if ycrop < 0:
                ycrop = 0
            if ycrop + hcrop > iheight:
                hcrop = iheight - ycrop

            blob["xcrop"] = xcrop
            blob["ycrop"] = ycrop
            blob["wcrop"] = wcrop
            blob["hcrop"] = hcrop

            blob["blobimage"] = img[ycrop:ycrop+hcrop, xcrop:xcrop+wcrop]
            blob["changed"] = self.checkintersection(x, y, w, h, rects_prev)

            mask = binary[ycrop:ycrop+hcrop, xcrop:xcrop+wcrop]
            blob["size"] = np.sum(mask < 255)
            kernel = np.ones((self.kernel_fast, self.kernel_fast), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel)
            blob["colors"] = reportcolors(blob["blobimage"], mask)
            blob["illumination"] = self.background[blob["ycenter"], blob["xcenter"]]

            blob["id"] = 0
            blob["filename"] = ""

            blob["age"] = 0
            blob["delay"] = 0
            blob["direction"] = ""
            blob["cost"] = ""
            blob["weights"] = ""

            blobs.append(blob)

            count = count + 1

        self.frame_id += 1
        return count, blobs, gray
