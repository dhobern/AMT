/* 
 * Protective end strip for panel of imaging surface for autonomous moth 
 * trap. See https://amt.hobern.net/ for more detail.
 *
 * Author: Donald Hobern
 * Copyright: Copyright 2021, Donald Hobern
 * License: CC0
 * Version: 1.0.0
 * Email: dhobern@gmail.com
 */

length = 150; 
height = 13;
width = 8.5;
cornerradius = 8;
extension = 5;
thickness = 2;

// To adjust design and ensure that the design is at least mostly manifold.
fudge = 0.1;
fudge2 = 0.2;

$fn = 360;

union() {
    difference() {
        // main block
        union() {
            translate([0, cornerradius, 0]) {
                cube([width + 2 * thickness, length - 2 * cornerradius, height]);
            }
            translate([0, 0, cornerradius]) {
                cube([width + 2 * thickness, length, height - cornerradius]);
            }
            for (i = [cornerradius, length - cornerradius]) {
                translate([0, i, cornerradius]) rotate([0, 90, 0]) {
                    cylinder(d = cornerradius * 2, h = width + 2 * thickness);
                }
            }
        }
        translate([-fudge, -fudge, height]) {
            cube([width + 2 * thickness + fudge2, length + fudge2, cornerradius + fudge]);
        }
    }
    for(i = [0, thickness + width]) {
        translate([i, 0, height - fudge]) {
           cube([thickness,  length, extension + fudge]);
        }
    }
}