/* 
 * End caps for AMT LED tubes
 *
 * This design produces the end caps for a tube containing 3, 6 or 9
 * high-power LEDs for the autonomous moth trap with spacing to hold 
 * an aluminium extruded channel for the LEDs. This design has
 * subsequently been replaced with a new version that uses a simple 
 * and cheaper aluminium bar in place of the channel. This change offers
 * a wider angle of view and greater heat sink capacity as well as
 * lowering the cost of the design. See https://amt.hobern.net/ for more
 * detail.
 *
 * The design produces two end caps, one of which has a hole for cable
 * entry. In the AMT implementation, a further 3D component is glued to
 * the outside of the cable hole to support attachment of a 2-pin
 * waterproof connector plug (https://amazon.com/gp/product/B016NV1PVW/).
 * See AMTMothLamp_CableSocket.scad.
 *
 * Author: Donald Hobern
 * Copyright: Copyright 2021, Donald Hobern
 * License: CC0
 * Version: 1.0.0
 * Email: dhobern@gmail.com
 */
 
height = 20;  
outerdiam = 35.1;
innerdiam = 30.8;
thickness = (outerdiam - innerdiam) / 2;
wall = 3;
platelength = 70;
platedepth = 5;
extension = (platelength - outerdiam - (2 * wall)) / 2;

railwidth = 25.2;
raildepth = 3.2;
railoffset = 5;

screwdiam = 5;

cablediam = 6.5;

fillet = 3;

// To adjust design and ensure that the design is at least mostly manifold.
fudge = 0.1;
fudge2 = 0.2;
fudge3 = 0.3;

$fn = 360;

for (ec = [0, outerdiam + wall + platedepth + 10]) {
    translate([0, ec, 0]) {

        difference() {
            
            // Main block 
            
            union() {
                cylinder(d = outerdiam + (2 * wall), h = height);
                
                translate([-(outerdiam / 2) - wall, -(outerdiam / 2), 0]) {
                    cube([outerdiam + 2 * wall, (outerdiam / 2), height]);
                }

                translate([-(fillet + wall + (outerdiam / 2)), platedepth - wall - (outerdiam / 2), 0]) {
                    difference() {
                        cube([fillet, fillet, height]);
                        translate([0, fillet, -fudge]) {
                            cylinder(h = height + fudge2, r = fillet);
                        }
                    }
                }

                translate([wall + (outerdiam / 2), platedepth - wall - (outerdiam / 2), 0]) {
                    difference() {
                        cube([fillet, fillet, height]);
                        translate([fillet, fillet, -fudge]) {
                            cylinder(h = height + fudge2, r = fillet);
                        }
                    }
                }

                // Base
                translate([-(extension + (outerdiam / 2) + wall), -((outerdiam / 2) + wall), 0]) {
                    translate([fillet, 0, 0]) {
                        cube([platelength - (2 * fillet), platedepth, height]);
                    }
                    translate([0, 0, fillet]) {
                        cube([platelength, platedepth, height - (2 * fillet)]);
                    }
                    for (i = [fillet, platelength - fillet]) {
                        for (j = [fillet, height - fillet]) {
                            translate([i, 0, j]) {
                                rotate([-90, 0, 0]) {
                                    cylinder (r = fillet, h = platedepth);
                                }
                            }
                        }
                    }
                }
            }
            
            // Remove outer channel
            translate([0, 0, wall]) {
                difference() {
                    translate([0, 0, -fudge]) {
                        cylinder(d = outerdiam, h = height + fudge);
                    }
                    cylinder(d = innerdiam, h = height + fudge3);
                }
            }
            
            // Remove inner channel for rail
            //   - railoffset makes better use of the available diameter
           
            translate([-(railwidth / 2), -(raildepth / 2) - railoffset, wall]) {
                cube([railwidth, raildepth, height]);
            }
            
            // Make screw holes
            for (i = [5 + (screwdiam / 2) - (platelength / 2), (platelength / 2) - 5 - (screwdiam / 2)]) {
                translate([i, -fudge - wall - outerdiam / 2, height / 2]) {
                    rotate([-90,0,0]) {
                        cylinder(h = platedepth + fudge2, d = screwdiam);
                    }
                }
            }

            // Make cable hole in one end cap
            if (ec == 0) {
                translate([0, 0, -fudge]) {
                    cylinder(d = cablediam, h = height + fudge2);
                }
            }
        }
    }
}