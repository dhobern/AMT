/* 
 * Spacer to hold aluminium bars rigid
 *
 * This design produces a bracket that holds two 25 x 3 mm aluminium bar
 * at the same separation as in AMT_PiZero_BaseBracket and additionally 
 * includes feet to the sides for support. See https://amt.hobern.net/ 
 * for more detail.
 *
 * Author: Donald Hobern
 * Copyright: Copyright 2021, Donald Hobern
 * License: CC0
 * Version: 1.0.0
 * Email: dhobern@gmail.com
 */

// From AMT_PiZero_BaseBracket 
length = 25; 
width = 121;
height = 80;
cornerradius = 6;
barwidth = 25.2;
bardepth = 3.2;
thickness = 3;
screwdiam = 5;

footlength = 30;
footwidth = 20;
screwrecessdiam = 10;
screwrecessdepth = 3;

centrelength = width + 2 * thickness;
mainlength = centrelength + 2 * footlength;

// To adjust design and ensure that the design is at least mostly manifold.
fudge = 0.1;
fudge2 = 0.2;

$fn = 360;

for (bb = [0, 20]) {
    translate([0, bb, 0]) {
        rotate([90, 0, 0]) {
            difference() {
                // main block
                union() {
                    cube([mainlength, footwidth, thickness]);
                    translate([(mainlength - centrelength) / 2, 0, 0]) {
                        cube([centrelength, footwidth, bardepth + 2 * thickness + screwrecessdepth]);
                    }
                }
                for (i = [(mainlength - centrelength) / 2 + thickness + cornerradius, (mainlength + centrelength) / 2 - thickness - cornerradius - barwidth]) {
                    translate([i, -fudge, thickness + screwrecessdepth]) {
                        cube([barwidth, footwidth + fudge2, bardepth]);
                    }
                }
                for (i = [(mainlength - centrelength) / 2 + thickness + cornerradius + barwidth / 2, (mainlength + centrelength) / 2 - thickness - cornerradius - barwidth / 2]) {
                    translate([i, footwidth / 2, -fudge]) {
                        cylinder(d = screwdiam, h = bardepth + 2 * thickness + screwrecessdepth + fudge2);
                        cylinder(d = screwrecessdiam, h = screwrecessdepth + fudge);
                    }
                }
                for (i = [footwidth /2, mainlength - footwidth / 2]) {
                    translate([i, footwidth / 2, - fudge]) {
                        cylinder(d = screwdiam, h = thickness + fudge2);
                    }
                }
            }
        }
    }
}