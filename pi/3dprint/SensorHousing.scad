fudge = 0.1;
fudge2 = fudge * 2;

length = 70;
width = 50;
height = 37;

toothheight = 3;
toothwidth = 3;
toothinset = 5;

wall = 8;
slits = 6;
plate = 3;

fillet = 4;

diam = 8;
spikediam = 2.5;
spikelength = 12;
spikespacing = 4;

translate([width, 0, 0]) {
    difference() {
        union() {
            translate([fillet, 0, 0]) {
                cube([width - 2 * fillet, length, plate]);
            }
            translate([0, fillet, 0]) {
                cube([width, length - 2 * fillet, plate]);
            }
            for(i = [fillet, width - fillet]) {
                for (j = [fillet, length - fillet]) {
                    translate([i, j, 0]) {
                        cylinder(r = fillet, h = plate, center = false, $fn = 360);
                    }
                }
            }
            translate([0, 0, plate * 2 - fudge]) rotate([-90, 0, 0]) {
                linear_extrude(height = length - plate - fudge2) {
                    polygon([[toothinset, 0],
                           [width - toothinset, 0],
                           [width - toothinset - toothwidth, toothheight - fudge],
                           [toothinset + toothwidth, toothheight - fudge]]);
                }
            }
            translate([toothinset, 0, plate * 2 - fudge]) {
                cube([width - 2 * toothinset, plate, height - wall - plate - fudge]);
            }
            
            translate([wall + fudge, plate - fudge, plate * 2 - fudge]) {
                cube([width - 2 * wall + fudge2, length - 3 * plate - diam + fudge, height - wall - 20]);
            }
            
            for (i = [-5, 4]) {
                translate([width/2 + i, plate - fudge, plate * 2 - fudge]) {
                    cube([1, length - 3 * plate - diam + fudge, height - wall - 17]);
                }
            }

            translate([width / 2, plate + spikediam / 2 + spikespacing, 2 * plate - fudge]) {
                cylinder(d = spikediam, h = height - plate - wall - fudge, center = false, $fn = 360);
            }
        }
        translate([width / 2, length - 2 * plate - diam / 2, -fudge]) {
            cylinder(d = diam, h = 2 * plate + fudge2, center = false, $fn = 360);
        }
    }
}

translate([0, 0, height]) {
    rotate([0, 180, 0]) {
        difference() {
            union() {
                difference() {
                    union() {
                        translate([-width / 2, 0, 0]) {
                            cube([width, length, height]);
                        }
                    }
                 
                    translate([wall - width / 2, plate, -fudge]) {
                        cube([width - 2 * wall, length - 2 * plate, height - wall + fudge]);
                    }
                    
                    slit = (length - 2 * wall) / (slits * 2);
                    for(i = [wall + slit / 2:slit * 2:length - wall - slit]) { 
                        translate([2 - width / 2, i, 2 * plate]) {
                            rotate([0, 0, 25]) {
                                translate([-(wall + 8) / 2, -slit / 2, 0]) {
                                    cube([wall + 8, slit, height - 4 * plate]);
                                }
                            }
                        }
                        translate([width / 2 - 2, i, 2 * plate]) {
                            rotate([0, 0, -25]) {
                                translate([-(wall + 8) / 2, -slit / 2, 0]) {
                                    cube([wall + 8, slit, height - 4 * plate]);
                                }
                            }
                        }
                        translate([0, i, height - wall / 2]) {
                            rotate([25, 0, 0]) {
                                translate([-width / 2 + wall + fudge, -slit / 2, -(wall + 5) / 2]) {
                                    cube([width - 2 * (wall + fudge), slit, wall + 5]);
                                }
                            }
                        }
                    }
                    for(i = [-fudge,width - fillet + fudge]) {
                        for(j = [-fudge, length - fillet + fudge]) {
                            translate([i - width / 2, j, -fudge]) {
                                cube([fillet + fudge, fillet + fudge, height + fudge2]);
                            }
                        }
                    }
                }

                for(i = [fillet, width - fillet]) {
                    for(j = [fillet, length - fillet]) {
                        translate([i - width / 2, j, 0]) {
                            cylinder(r = fillet, h = height, center = false, $fn = 360);
                        }
                    }
                }
            }
                    
            translate([-width / 2, -fudge, toothheight - fudge]) {
                rotate([-90, 0, 0]) {
                    linear_extrude(height = length - plate - fudge) {
                       polygon([[toothinset, 0],
                              [width - toothinset, 0],
                              [width - toothinset - toothwidth, toothheight],
                              [toothinset + toothwidth, toothheight]]);
                    }
                }
            }
            
            translate([-width / 2 + toothinset, -fudge, plate - fudge2]) {
                cube([width - 2 * toothinset, plate + fudge2, height - plate - wall + fudge2]);
            }
        }
    }
}
