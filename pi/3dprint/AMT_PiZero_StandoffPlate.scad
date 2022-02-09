thickness = 3;
rubberdepth = 1.5;

fudge = 0.1;
fudge2 = 0.2;
fudge3 = 0.3;

margin = 3;

screwx = 115;
screwy = 182;
screwdiam = 3.3;

x = screwx + screwdiam + 2 * margin;
y = screwy + screwdiam + 2 * margin;

cameraoffset = 118; /* from lower screw centres */
camerascrewgap = 30;
camerabasegap = 45;
cameradiam = 35;
lensdiam = 31;
piscrewdiam = 2.9;

cameray = cameraoffset + y - screwy;

pizeroscrewx = 23;
pizeroscrewy = 58;

pizerow = pizeroscrewx + piscrewdiam + 2 * margin;
pizerol = pizeroscrewy + piscrewdiam + 2 * margin;
pizerox = 7;
pizeroy = (screwy / 2 - pizerol) + margin;

rtcscrewx = 18;
rtcscrewy = 25;

rtcw = rtcscrewx + piscrewdiam + 2 * margin;
rtcl = rtcscrewy + piscrewdiam + 2 * margin;
rtcx = 6.5;
rtcy = 150;

boardscrewx = 46;
boardscrewy = 66;

boardw = boardscrewx + piscrewdiam + 2 * margin;
boardl = boardscrewy + piscrewdiam + 2 * margin;
boardx = 55;
boardy = 2 * margin + screwdiam;

midwidth = 134;
middiam = 16;

rise = 4.5;

$fn = 360;

difference() {
    union() {
        difference() {
            cube([x, y, thickness]);
            translate([2 * margin + screwdiam, 2 * margin + screwdiam, -fudge]) {     
                cube([x - screwdiam * 2 - 4 * margin, y - screwdiam * 2 - 4 * margin, thickness + fudge2]);
            }
        }
        translate([0, y / 2 - screwdiam / 2 - margin, 0]) {
            cube([x, screwdiam + 2 * margin, thickness]);
        }
        for (i = [x / 3, 2 * x / 3]) {
            for (j = [margin + screwdiam / 2, y / 2, y - margin - screwdiam / 2]) {
                translate([i, j, 0]) {
                    cylinder(d = 2 * margin, h = thickness + rise);
                }
            }
        }                
        for (i = [margin + screwdiam / 2, x - margin - screwdiam / 2]) {
            for (j = [y / 3, 2 * y / 3]) {
                translate([i, j, 0]) {
                    cylinder(d = 2 * margin, h = thickness + rise);
                }
            }
        }
        for (i = [(x - camerabasegap) / 2 - 2 * margin - screwdiam / 2 , (x + camerabasegap) / 2 - 2 * margin - screwdiam / 2]) {
            translate([i, y / 2, 0]) {
                cube([screwdiam + 4 * margin, y / 2, thickness]);
            }
        } 
        for (i = [(x - camerabasegap) / 2 + margin, (x + camerabasegap) / 2 - margin]) {
            for (j = [cameray - camerabasegap / 2 + 2 *     margin, cameray + camerabasegap / 2 - 2 * margin]) {
                translate([i, j, 0]) {
                    cylinder(d = margin, h = thickness + rise);
                }
            }
        }
        translate([x / 2, cameray, 0]) {
            cylinder(d = lensdiam + 2 * margin, h = thickness + rise - rubberdepth);
        }
    
        translate([pizerox, pizeroy, 0]) {
            difference() {
                union() {
                    cube([pizerow, pizerol, thickness]);
                    translate([pizerow / 2 - margin, -((screwy /2) - pizerol), 0]) {
                        cube([2 * margin, (screwy / 2) - pizerol, thickness]);
                    }
                    for (i = [margin + piscrewdiam / 2, pizerow - margin - piscrewdiam / 2]) {
                        translate([i, pizerol / 2, 0]) {
                            cylinder(d = margin, h = thickness + rise);
                        }
                    }
                }
                translate([2 * margin + piscrewdiam, 2 * margin + piscrewdiam,, -fudge]) {
                    cube([pizerow - 4 * margin - 2 * piscrewdiam, pizerol - 4 * margin - 2 * piscrewdiam, thickness + fudge2]);
                }
                for (i = [margin + piscrewdiam / 2, pizerow - margin - piscrewdiam /2]) {
                    for (j = [margin + piscrewdiam / 2, pizerol - margin - piscrewdiam /2]) {
                        translate([i, j, -fudge]) {
                            cylinder(d = piscrewdiam, h = thickness + fudge2);
                        }
                    }
                }
            }
        }
        
        translate([rtcx, rtcy, 0]) {
            difference() {
                union() {
                    cube([rtcw, rtcl, thickness]);
               }
                translate([2 * margin + piscrewdiam, 2 * margin + piscrewdiam,, -fudge]) {
                    cube([rtcw - 4 * margin - 2 * piscrewdiam, rtcl - 4 * margin - 2 * piscrewdiam, thickness + fudge2]);
                }
                for (i = [margin + piscrewdiam / 2, rtcw - margin - piscrewdiam /2]) {
                    for (j = [margin + piscrewdiam / 2, rtcl - margin - piscrewdiam /2]) {
                        translate([i, j, -fudge]) {
                            cylinder(d = piscrewdiam, h = thickness + fudge2);
                        }
                    }
                }
            }
        }

        translate([boardx, boardy, 0]) {
            difference() {
                union() {
                    cube([boardw, boardl, thickness]);
                    translate([-6 * margin, boardl / 2 - margin, 0]) {
                        cube([boardw + 8 * margin, 2 * margin, thickness]);
                    }
                    translate([boardw / 2 - margin, -3 * margin, 0]) {
                        cube([2 * margin, boardl + 6 * margin, thickness]);
                    }
                    for (i = [margin + piscrewdiam / 2, boardw - margin - piscrewdiam / 2]) {
                        translate([i, boardl / 2, 0]) {
                            cylinder(d = margin, h = thickness + rise);
                        }
                    }
                }
                translate([2 * margin + piscrewdiam, 2 * margin + piscrewdiam, -fudge]) {
                    cube([boardw - 4 * margin - 2 * piscrewdiam, boardl - 4 * margin - 2 * piscrewdiam, thickness + fudge2]);
                }
                for (i = [margin + piscrewdiam / 2, boardw - margin - piscrewdiam /2]) {
                    for (j = [margin + piscrewdiam / 2, boardl - margin - piscrewdiam /2]) {
                        translate([i, j, -fudge]) {
                            cylinder(d = piscrewdiam, h = thickness + fudge2);
                        }
                    }
                }
            }
        }
    }

    
    for (i = [margin + screwdiam / 2, x - margin - screwdiam / 2]) {
        for (j = [margin + screwdiam / 2, y - margin - screwdiam / 2]) {
            translate([i, j, -fudge]) {
                cylinder(d = screwdiam, h = thickness + fudge2);
            }
        }
    }
    
    for (i = [(x - midwidth) / 2, (x + midwidth) / 2]) {
        translate([i, y / 2, -fudge]) {
            cylinder(d = middiam, h = thickness + fudge2);
        }
    }
    
    translate([x / 2, cameray, -fudge]) {
        cylinder(d = lensdiam, h = thickness + rise + fudge2);
    }

    for (i = [(x - camerabasegap) / 2, (x + camerabasegap) / 2]) {
        for (j = [cameray - camerabasegap / 2, cameray + camerabasegap / 2]) {
            translate([i, j, -fudge]) {
                cylinder(d = screwdiam, h = thickness + fudge2);
            }
        }
    }
}
