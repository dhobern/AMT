/* 
 * Bracket to support imaging surface for automonous moth trap
 *
 * This design produces a bracket that holds two 25 x 3 mm aluminium bar
 * at the same separation as in AMT_PiZero_BaseBracket and two vertical
 * bars to support the imaging surface. See https://amt.hobern.net/ 
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
screwinset = 8;

footlength = 30;
footwidth = 35;
screwrecessdiam = 10;
screwrecessdepth = 3;

riserheight = 40;

centrelength = width + 2 * thickness;
mainlength = centrelength + 2 * footlength;

// To adjust design and ensure that the design is at least mostly manifold.
fudge = 0.1;
fudge2 = 0.2;

$fn = 360;

difference() {
    // main block
    union() {
        cube([mainlength, footwidth, thickness]);
        translate([(mainlength - centrelength) / 2, 0, 0]) {
            cube([centrelength, footwidth, bardepth + 2 * thickness + screwrecessdepth]);
        }
        translate([0, footwidth, 0]) {
            cube([mainlength, bardepth + 4 * thickness, riserheight]);
        }
    }
    for (i = [(mainlength - centrelength) / 2 + thickness + cornerradius, (mainlength + centrelength) / 2 - thickness - cornerradius - barwidth]) {
        translate([i, -fudge, thickness + screwrecessdepth]) {
            cube([barwidth, footwidth + fudge2, bardepth + thickness + fudge]);
        }
    }
    for (i = [screwinset, mainlength - screwinset - barwidth]) {
        translate([i, footwidth + 2 * thickness, riserheight - footwidth]) {
            cube([barwidth, bardepth, footwidth + fudge]);
        }
    }
    for (i = [(mainlength - centrelength) / 2 + thickness + cornerradius + barwidth / 2, (mainlength + centrelength) / 2 - thickness - cornerradius - barwidth / 2]) {
        translate([i, footwidth / 2, -fudge]) {
            cylinder(d = screwdiam, h = bardepth + 2 * thickness + screwrecessdepth + fudge2);
            cylinder(d = screwrecessdiam, h = screwrecessdepth + fudge);
        }
    }
    for (i = [(mainlength - centrelength) / 2 + thickness + cornerradius + barwidth + screwinset, (mainlength + centrelength) / 2 - thickness - cornerradius - barwidth - screwinset]) {
        for(j = [screwinset, footwidth - screwinset]) {
            translate([i, j, -fudge]) {
                cylinder(d = screwdiam, h = bardepth + 2 * thickness + screwrecessdepth + fudge2);
                cylinder(d = screwrecessdiam, h = screwrecessdepth + fudge);
            }
        }
    }
    for (i = [footwidth /2, mainlength - footwidth / 2]) {
        translate([i, footwidth / 2, - fudge]) {
            cylinder(d = screwdiam, h = thickness + fudge2);
        }
    }
    for (i = [screwinset + barwidth / 2, mainlength - screwinset - barwidth / 2]) {
        translate([i, footwidth - fudge, riserheight - footwidth / 2]) rotate([-90, 0, 0]) {
            cylinder(d = screwdiam, h = bardepth + 4 * thickness + fudge2);
            cylinder(d = screwrecessdiam, h = screwrecessdepth + fudge);
            translate([0, 0, bardepth + 4 * thickness - screwrecessdepth]) {
                cylinder(d = screwrecessdiam, h = screwrecessdepth + fudge2);
            }
        }
    }
}

translate([0, -footwidth - thickness, , 0]) {
    difference() {
        translate([(mainlength - centrelength) / 2, 0, 0]) {
            union() {
                cube([centrelength, footwidth, 2 * thickness]);
                for(i = [thickness + cornerradius, centrelength - thickness - cornerradius - barwidth]) {
                    translate([i + fudge, 0, 0]) {
                        cube([barwidth - fudge2, footwidth, 3 * thickness]);
                    }
                }
            }
        }
        for (i = [(mainlength - centrelength) / 2 + thickness + cornerradius + barwidth / 2, (mainlength + centrelength) / 2 - thickness - cornerradius - barwidth / 2]) {
            translate([i, footwidth / 2, -fudge]) {
                cylinder(d = screwdiam, h = bardepth + 2 * thickness + screwrecessdepth + fudge2);
                cylinder(d = screwrecessdiam, h = screwrecessdepth + fudge);
            }
        }
        for (i = [(mainlength - centrelength) / 2 + thickness + cornerradius + barwidth + screwinset, (mainlength + centrelength) / 2 - thickness - cornerradius - barwidth - screwinset]) {
                for(j = [screwinset, footwidth - screwinset]) {
                    translate([i, j, -fudge]) {
                        cylinder(d = screwdiam, h = bardepth + 2 * thickness + screwrecessdepth + fudge2);
                        cylinder(d = screwrecessdiam, h = screwrecessdepth + fudge);
                }
            }
        }
    }    
}
