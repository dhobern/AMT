/* 
 * AMTMothLamp_CableSocked.scad - Cable adaptor for AMT LED tubes
 *
 * This design is intended to be glued to the cable end of an end cap 
 * from the AMTMothLamp_EndCaps.scad design(s). 
 *
 * See AMTMothLamp_CableSocket.scad.
 *
 * See https://amt.hobern.net/ for more detail.
 *
 * Author: Donald Hobern
 * Copyright: Copyright 2021, Donald Hobern
 * License: CC0
 * Version: 1.0.0
 * Email: dhobern@gmail.com
 */

diam1 = 30;
diam2 = 18;

length = 15.3;
width = 9.5;
depth = 13;

// To adjust design and ensure that the design is at least mostly manifold.
fudge = 0.1;
fudge2 = fudge * 2;

$fn = 360;

difference() {
   cylinder(d1 = diam1, d2 = diam2, h = depth);
    
    for (i = [(length - width) / 2, (width - length) / 2]) {
        translate([i, 0, -fudge]) {
            cylinder(d = width, h = depth + fudge2);
        }
    }

    translate([(-length + width) / 2, -width / 2, -fudge]) {
        cube([length - width, width, depth + fudge2]);
    }
}
