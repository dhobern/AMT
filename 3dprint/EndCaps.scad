height = 20;
outerdiam = 35.1;
innerdiam = 30.8;
thickness = (outerdiam - innerdiam) / 2;
wall = 3;
platelength = 70;
platedepth = 5;
extension = (platelength - outerdiam - (2 * wall)) / 2;

railwidth = 28.5;
railbody = 24.1;
raildepth = 10.5;
railflange = 1.2;
railoffset = 2;

screwdiam = 5;

cablediam = 6.5;

fillet = 3;

fudge = 0.1;
fudge2 = 0.2;
fudge3 = 0.3;

for (i = [0, outerdiam + wall + platedepth + 10]) {
    translate([0, i, 0]) {

        difference() {
            
            // Main block 
            
            union() {
                cylinder(d = outerdiam + (2 * wall), h = height, center=false, $fn = 360);
                
                translate([-(outerdiam / 2) - wall, -(outerdiam / 2), 0]) {
                    cube([outerdiam + 2 * wall, (outerdiam / 2), height]);
                }

                translate([-(fillet + wall + (outerdiam / 2)), platedepth - wall - (outerdiam / 2), 0]) {
                    difference() {
                        cube([fillet, fillet, height]);
                        translate([0, fillet, -fudge]) {
                            cylinder(h = height + fudge2, r = fillet, center = false, $fn = 360);
                        }
                    }
                }

                translate([wall + (outerdiam / 2), platedepth - wall - (outerdiam / 2), 0]) {
                    difference() {
                        cube([fillet, fillet, height]);
                        translate([fillet, fillet, -fudge]) {
                            cylinder(h = height + fudge2, r = fillet, center = false, $fn = 360);
                        }
                    }
                }

                translate([-(extension + (outerdiam / 2) + wall), -((outerdiam / 2) + wall), 0]) {
                    translate([fillet, 0, 0]) {
                        cube([platelength - (2 * fillet), platedepth, height]);
                    }
                    translate([0, 0, fillet]) {
                        cube([platelength, platedepth, height - (2 * fillet)]);
                    }
                    translate([fillet, 0, fillet]) {
                        rotate([-90, 0, 0]) {
                            cylinder (r = fillet, h = platedepth, center = false, $fn = 360);
                        }
                    }
                    translate([platelength - fillet, 0, fillet]) {
                        rotate([-90, 0, 0]) {
                            cylinder (r = fillet, h = platedepth, center = false, $fn = 360);
                        }
                    }
                    translate([fillet, 0, height - fillet]) {
                        rotate([-90, 0, 0]) {
                            cylinder (r = fillet, h = platedepth, center = false, $fn = 360);
                        }
                    }
                    translate([platelength - fillet, 0, height - fillet]) {
                        rotate([-90, 0, 0]) {
                            cylinder (r = fillet, h = platedepth, center = false, $fn = 360);
                        }
                    }
                }
            }
            
            // Remove outer channel
            
            translate([0, 0, wall]) {
                difference() {
                    translate([0, 0, -fudge]) {
                        cylinder(d = outerdiam, h = height + fudge, center = false, $fn = 360);
                    }
                    cylinder(d = innerdiam, h = height + fudge3, center = false, $fn = 360);
                }
            }
            
            // Remove inner channel for rail
            //   - railoffset makes better use of the available diameter
           
            translate([-(railwidth / 2), (raildepth / 2) - railflange - railoffset, wall]) {
                cube([railwidth, railflange, height]);
            }
            translate([-(railbody / 2), -(raildepth / 2) - railoffset, wall]) {
                cube([railbody, raildepth, height]);
            }
            
            // Make screw holes
            translate([5 + (screwdiam / 2) - (platelength / 2), -fudge - wall - outerdiam / 2, height / 2]) {
                rotate([-90,0,0]) {
                    cylinder(h = platedepth + fudge2, d = screwdiam, center = false, $fn = 360);
                }
            }
            translate([(platelength / 2) - 5 - (screwdiam / 2), -fudge - wall - outerdiam / 2, height / 2]) {
                rotate([-90,0,0]) {
                    cylinder(h = platedepth + fudge2, d = screwdiam, center = false, $fn = 360);
                }
            }

            // Make cable hole
            if (i == 0) {
                translate([0, 0, -fudge]) {
                    cylinder(d = cablediam, h = height + fudge2, center = false, $fn = 360);
                }
            }
        }
    }
}
