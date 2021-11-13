/* 
 * Base bracket for Pi Zero in 171 x 121 x 80 mm enclosure
 *
 * This design produces a bracket that can be screwed/glued to one end
 * of the enclosure and that receives two 25 x 3 mm aluminium bar to space 
 * and level it relative to the illuminated surface. See
 * https://amt.hobern.net/ for more detail.
 *
 * Author: Donald Hobern
 * Copyright: Copyright 2021, Donald Hobern
 * License: CC0
 * Version: 1.0.0
 * Email: dhobern@gmail.com
 */
 
length = 25; 
width = 121;
height = 80;

cornerradius = 6;

barwidth = 25.2;
bardepth = 3.2;

thickness = 3;
screwdiam = 5;

// To adjust design and ensure that the design is at least mostly manifold.
fudge = 0.1;
fudge2 = 0.2;

$fn = 360;

difference() {
    // main block
    cube([width + 2 * thickness, length + bardepth + 2 * thickness, height]);

    // Carve the interior as two cubes of different width and two cylinders
    // for the rounded corners
    translate([thickness, bardepth + 2 * thickness + cornerradius, -fudge]) {
        cube([width, length - cornerradius + fudge, height + fudge2]);
    }
    translate([thickness + cornerradius, bardepth + 2 * thickness, -fudge]) {
        cube([width - 2 * cornerradius, cornerradius + fudge, height + fudge2]);
    }
    for (i = [thickness + cornerradius, thickness + width - cornerradius]) {
        translate([i, bardepth + 2 *  thickness + cornerradius, -fudge]) {
            cylinder(r = cornerradius, h = height + fudge2);
        }
    }
    
    // Slots for aluminium bars
    for (i = [thickness + cornerradius, thickness + width - cornerradius - barwidth]) {
        translate([i, thickness, height / 2]) {
            cube([barwidth, bardepth, height / 2 + fudge]);
        }
    }
    
    // Screw holes for sides
    for (i = [0, width + thickness]) {
        translate([i - fudge, bardepth + length - screwdiam / 2, height * 0.75]) rotate([0, 90, 0]) {
            cylinder(d = screwdiam, h = thickness + fudge2);
        }
    }
    
    // Screw holes for optionally securing the aluminium rods
    for (i = [thickness + cornerradius + barwidth / 2, width + thickness - cornerradius - barwidth / 2]) {
        translate([i, -fudge, height * 0.75]) rotate([-90, 0, 0]) {
            cylinder(d = screwdiam, h = bardepth + 2 * thickness + fudge2);
        }
    }
}