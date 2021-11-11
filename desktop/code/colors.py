#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 22 September 2021

@author: dhobern
"""
import numpy as np
import cv2

def getcount(hist, size, color, mindiff, maxdiff):
    count = 0
    for r in range(size):
        for g in range(size):
            for b in range(size):
                if (color == "R" and r >= g + b + mindiff and abs(g - b) <= maxdiff) or \
                    (color == "G" and g >= r + b + mindiff and abs(r - b) <= maxdiff) or \
                    (color == "B" and b >= r + g + mindiff and abs(r - g) <= maxdiff) or \
                    (color == "C" and r <= g + b - size - mindiff + 1 and abs(g - b) <= maxdiff) or \
                    (color == "M" and g <= r + b - size - mindiff + 1 and abs(r - b) <= maxdiff) or \
                    (color == "Y" and b <= r + g - size - mindiff + 1 and abs(r - g) <= maxdiff) or \
                    (color == "W" and r + b + g >= 3 * (size - 1) - 2 * maxdiff and abs(r - g) <= maxdiff and abs(b - g) <= maxdiff and abs(r - b) <= maxdiff) or \
                    (color == "K" and r + b + g <= 2 * maxdiff and abs(r - g) <= maxdiff and abs(b - g) <= maxdiff and abs(r - b) <= maxdiff):
                        count += hist[b][g][r]
    return count    

def reportcolors(image, mask = None):
    colors = ""
    h, w, channels = image.shape
    pixels = h * w
    if mask is not None:
        image = image.copy()
        image[mask == 255] = 0
        alpha = np.sum(mask == 255)
        pixels -= alpha

    if pixels > 0:
        threshold = 0.02
        size = 2
        hist = cv2.calcHist([image], [0, 1, 2], None, [size, size, size], [0, 256, 0, 256, 0, 256])
        if hist[0][0][size - 1] / pixels > threshold:
            colors += "R"
        if hist[0][size - 1][0] / pixels > threshold:
            colors += "G"
        if hist[size - 1][0][0] / pixels > threshold:
            colors += "B"
        if hist[size - 1][size - 1][0] / pixels > threshold:
            colors += "C"
        if hist[size - 1][0][size - 1] / pixels > threshold:
            colors += "M"
        if hist[0][size - 1][size - 1] / pixels > threshold:
            colors += "Y"
        if hist[size - 1][size - 1][size - 1] / pixels > threshold:
            colors += "W"
        if (hist[0][0][0] - alpha) / pixels > threshold:
            colors += "K"
        if False:
            for c in [ "R", "G", "B", "C", "M", "Y", "W", "K" ]:
                count = getcount(hist, size, c, mindiff, maxdiff)
                if c == "W":
                    count - alpha
                if count / pixels > threshold:
                    colors += c

    return colors
