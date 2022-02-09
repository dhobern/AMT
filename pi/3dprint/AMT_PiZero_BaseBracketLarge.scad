/* 
 * Base bracket for Pi Zero in 222 x 146 x 75 mm enclosure
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
width = 146;
height = 75;

barspacing = 92.8;

cornerradius = 5;

barwidth = 25.5;
bardepth = 3.4;
slotdepth = 40;

thickness = 3;
screwdiam = 5;

// To adjust design and ensure that the design is at least mostly manifold.
fudge = 0.1;
fudge2 = 0.2;

$fn = 360;

module bcube(x=10, y=10, z=10, bt=2, bb=0, bs=2) {
   f = 0.1;
    difference() {
        cube([x, y, z]);
        translate([0,0,-f]) linear_extrude(height=z+2*f) {
            polygon([[-f,-f],[bs+f,-f],[-f,bs+f]]);
            polygon([[x-bs-f,-f],[x+f,-f],[x+f,bs+f]]);
            polygon([[x-bs-f,y+f],[x+f,y+f],[x+f,y-bs-f]]);
            polygon([[-f,y+f],[bs+f,y+f],[-f,y-bs-f]]);
        }
        rotate([0,90,0]) translate([0,0,-f]) linear_extrude(height=x+2*f) {
            polygon([[f,-f],[-bb-f,-f],[-f,bb+f]]);
            polygon([[-z-f,-f],[-z-f,bt+f],[-z+bt+f,-f]]);
            polygon([[f,y+f],[-bb-f,y+f],[f,y-bb-f]]);
            polygon([[-z-f,y+f],[-z-f,y-bt-f],[-z+bt+f,y+f]]);
        }
        rotate([-90,0,0]) translate([0,0,-f]) linear_extrude(height=y+2*f) {
            polygon([[-f,f],[bb+f,f],[-f,-bb-f]]);
            polygon([[x-bb-f,f],[x+f,f],[x+f,-bb-f]]);
            polygon([[-f,-z-f],[bt+f,-z-f],[-f,-z+bt+f]]);
            polygon([[x-bt-f,-z-f],[x+f,-z-f],[x+f,-z+bt+f]]);
        }
    }
}

difference() {
    // main block
    bcube(x = width + 2 * thickness, y = length + bardepth + 3 * thickness, z = height, bb = 2, bt = 2, bs = thickness);

    // Carve the interior as two cubes of different width and two cylinders
    // for the rounded corners
    translate([thickness, bardepth + 3 * thickness + cornerradius, -fudge]) {
        cube([width, length - cornerradius + fudge, height + fudge2]);
    }
    translate([thickness + cornerradius, bardepth + 3 * thickness, -fudge]) {
        cube([width - 2 * cornerradius, cornerradius + fudge, height + fudge2]);
    }
    for (i = [thickness + cornerradius, thickness + width - cornerradius]) {
        translate([i, bardepth + 3 * thickness + cornerradius, -fudge]) {
            cylinder(r = cornerradius, h = height + fudge2);
        }
    }
    
    // Slots for aluminium bars
    for (i = [thickness + (width - barspacing - barwidth) / 2, thickness + (width + barspacing - barwidth) / 2]) {
        translate([i, 2 * thickness, thickness + height - slotdepth]) {
            cube([barwidth, bardepth, slotdepth + fudge]);
        }
        translate([i - 2, 2 * thickness - 2, height - 2]) {
            bcube(x = barwidth + 4, y = bardepth + 4, z = 3 * thickness, bb = 2, bs = 2, bt = 2);
        }
    }
    
    // Screw holes for sides
    for (i = [0, width + thickness]) {
        translate([i - fudge, bardepth + length - screwdiam / 2, height * 0.75]) rotate([0, 90, 0]) {
            cylinder(d = screwdiam, h = thickness + fudge2);
        }
    }
    
    // Screw hole for underside
    translate([thickness + width / 2, -fudge, height * 0.75]) rotate([-90, 0, 0]) {
        cylinder(d = screwdiam, h = bardepth + 3 * thickness + fudge2);
        cylinder(d = screwdiam + 4 * thickness, h = thickness + fudge);
    }
    
    // Screw holes for optionally securing the aluminium rods
    for (i = [thickness + (width - barspacing) / 2, thickness + (width + barspacing) / 2]) {
        translate([i, -fudge, height * 0.75]) rotate([-90, 0, 0]) {
            cylinder(d = screwdiam, h = bardepth + 3 * thickness + fudge2);
            cylinder(d = screwdiam + 4 * thickness, h = thickness + fudge);
        }
    }
}

/*
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
*/