/* 
 * Template for holes for bracket to fix object on vertical 25 * 3 mm
 * aluminium bar
 *
 * This design produces a bracket that fits over a 25 x 3 mm aluminium bar.
 * See https://amt.hobern.net/ for more detail.
 *
 * Author: Donald Hobern
 * Copyright: Copyright 2021, Donald Hobern
 * License: CC0
 * Version: 1.0.0
 * Email: dhobern@gmail.com
 */

// From AMT_PiZero_BaseBracket 

yrange = 12.5;
xrange = 47.7;
xspacing = 145.8;
screwdiam = 2.5;
margin = 2;

thickness = 2.5;

notchl = 5;
notchw = 1.5;

length = xspacing + xrange + screwdiam + 2 * margin; 
width = yrange + screwdiam + 2 * margin;

// To adjust design and ensure that the design is at least mostly manifold.
fudge = 0.1;
fudge2 = 0.2;

$fn = 360;

difference() {
    cube([length, width, thickness]);
    for (i = [0, xrange, xspacing, xspacing + xrange]) {
        for(j = [0, yrange]) {
            translate([i + margin + screwdiam / 2, j + margin + screwdiam / 2, -fudge]) {
                cylinder(d = screwdiam, h = thickness + fudge2);
            }
        }
    }
    for (i = [0, length / 2, length]) {
        translate([i - notchl / 2, (width - notchw) / 2, -fudge]) {
            cube([notchl, notchw, thickness + fudge2]);
        }
    }
    for (i = [0, width / 2, width]) {
        translate([(length - notchw) / 2, i - notchl / 2, -fudge]) {
            cube([notchw, notchl, thickness + fudge2]);
        }
    }
}