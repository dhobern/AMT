/* 
 * Weather shield for temperature/humidity sensor DHT22
 *
 * This design produces a shield to protect a DHT22 sensor. See
 * https://amt.hobern.net/ for more detail.
 *
 * Author: Donald Hobern
 * Copyright: Copyright 2021, Donald Hobern
 * License: CC0
 * Version: 1.0.0
 * Email: dhobern@gmail.com
 */

outerdiameter = 80;
innerdiameter = 60;
height = 40;

sensorheight = 45;

roddiam = 10;

cablediam = 6;

// To adjust design and ensure that the design is at least mostly manifold.
fudge = 0.1;
fudge2 = 0.2;

$fn = 360;

rotate([90, 0, 0]) {
    difference() {
        // main block
        union() {
            cube([length, width, outerthickness]);
            translate([(length - centrelength) / 2, 0, 0]) {
                cube([centrelength, width, bardepth + 3 * thickness + clearance]);
            }
        }
        translate([(length - barwidth) / 2, -fudge, 2 * thickness + clearance]) {
            cube([barwidth, width + fudge2, bardepth]);
        }
        for (i = [(length - centrelength) / 4, length - (length - centrelength) / 4]) {
            for(j = [width * 0.25, width * 0.75]) {
                translate([i, j, -fudge]) {
                    cylinder(d = screwdiam, h = outerthickness + fudge2);
                }
            }
        }
    }
}