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
length = 60; 
width = 25;

// Slightly looser than for the tightly clamped fittings
barwidth = 25.3;
bardepth = 3.3;
barmargin = 5;
thickness = 2;
outerthickness = 4;
screwdiam = 2.5;

clearance = 2;

centrelength = barwidth + 2 * barmargin;

// To adjust design and ensure that the design is at least mostly manifold.
fudge = 0.1;
fudge2 = 0.2;

$fn = 360;

difference() {
    // main block
    union() {
        cube([length, width, outerthickness]);
    }
    translate([(length - barwidth) / 2, -fudge, thickness]) {
        cube([barwidth, width + fudge2, bardepth]);
    }
    for (i = [(length - centrelength) / 4, length - (length - centrelength) / 4]) {
        for(j = [width * 0.25, width * 0.75]) {
            translate([i, j, -fudge]) {
                cylinder(d = screwdiam, h = outerthickness +fudge2);
            }
        }
    }
}