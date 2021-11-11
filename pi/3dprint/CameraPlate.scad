fudge = 0.1;
fudge2 = 0.2;

screwdiam = 4;
screwspacex = 110;
screwspacey = 25;

rimwidth = 3;
rimheight = 3;

x = screwspacex + (2 * rimwidth) + screwdiam;
y = screwspacey + (2 * rimwidth) + screwdiam;

camheight = 26;
camlength = 102.2;
camwidth = 27.4;

wall = 2;

platedepth = 4;
platex = camlength + (4 * wall);
platey = camwidth + (2 * wall);

pegheight = 7;

columndiam = 8;
upperscrewdiam = 3.5;

rodspace = 50;
rodoffset = 55;

difference() {
    union() {
        translate([-platex / 2, -platey / 2, 0]) {
            cube([platex, platey, camheight - pegheight]);
        }
        translate([-x / 2, -y / 2, 0]) {
            cube([x, y, platedepth]);
        }
        translate([-(x / 2), -(y / 2), 0]) {
            cube([screwdiam + (2 * rimwidth), screwdiam + (2 * rimwidth), platedepth + 3]);
        } 
        translate([(x / 2) - screwdiam - (2 * rimwidth), -(y / 2), 0]) {
            cube([screwdiam + (2 * rimwidth), screwdiam + (2 * rimwidth), platedepth + 3]);
        } 
        translate([-(x / 2), (y / 2) - screwdiam - (2 * rimwidth), 0]) {
            cube([screwdiam + (2 * rimwidth), screwdiam + (2 * rimwidth), platedepth + 3]);
        } 
        translate([(x / 2) - screwdiam - (2 * rimwidth), (y / 2) - screwdiam - (2 * rimwidth), 0]) {
            cube([screwdiam + (2 * rimwidth), screwdiam + (2 * rimwidth), platedepth + 3]);
        } 
        translate([-camlength / 3, -(platey / 2) - (columndiam / 2) + wall, 0]) {
            difference() {
                union() {
                    cylinder(d = columndiam, h = camheight - pegheight, center = false, $fn = 360);
                    translate([-columndiam / 2, 0, 0]) {
                        cube([columndiam, columndiam / 2, camheight - pegheight]);
                    }
                }
                translate([0, 0, -fudge]) {
                    cylinder(d = upperscrewdiam, h = camheight - pegheight + fudge2, center = false, $fn = 360);
                }
            }
        } 
        translate([camlength / 3, -(platey / 2) - (columndiam / 2) + wall, 0]) {
            difference() {
                union() {
                    cylinder(d = columndiam, h = camheight - pegheight, center = false, $fn = 360);
                    translate([-columndiam / 2, 0, 0]) {
                        cube([columndiam, columndiam / 2, camheight - pegheight]);
                    }
                }
                translate([0, 0, -fudge]) {
                    cylinder(d = upperscrewdiam, h = camheight - pegheight + fudge2, center = false, $fn = 360);
                }
            }
        } 
        translate([-camlength / 3, (platey / 2) + (columndiam / 2) - wall, 0]) {
            difference() {
                union() {
                    cylinder(d = columndiam, h = camheight - pegheight, center = false, $fn = 360);
                    translate([-columndiam / 2, -columndiam / 2, 0]) {
                        cube([columndiam, columndiam / 2, camheight - pegheight]);
                    }
                }
                translate([0, 0, -fudge]) {
                    cylinder(d = upperscrewdiam, h = camheight - pegheight + fudge2, center = false, $fn = 360);
                }
            }
        } 
        translate([camlength / 3, (platey / 2) + (columndiam / 2) - wall, 0]) {
            difference() {
                union() {
                    cylinder(d = columndiam, h = camheight - pegheight, center = false, $fn = 360);
                    translate([-columndiam / 2, -columndiam / 2, 0]) {
                        cube([columndiam, columndiam / 2, camheight - pegheight]);
                    }
                }
                translate([0, 0, -fudge]) {
                    cylinder(d = upperscrewdiam, h = camheight - pegheight + fudge2, center = false, $fn = 360);
                }
            }
        } 
    }
    translate([-(camlength - camwidth) / 2, -camwidth / 2, -fudge]) {
        cube([camlength - camwidth, camwidth, camheight - pegheight + fudge2]);
    } 
    translate([-(camlength - camwidth) / 2, 0, -fudge]) {
        cylinder(d = camwidth, h = camheight - pegheight + fudge2, center = false, $fn = 360);
    } 
    translate([(camlength - camwidth) / 2, 0, -fudge]) {
        cylinder(d = camwidth, h = camheight - pegheight + fudge2, center = false, $fn = 360);
    } 
    translate([-screwspacex / 2, -screwspacey / 2, -fudge]) {
        cylinder(d = screwdiam, h = camheight, center = false, $fn =360);
    }
    translate([screwspacex / 2, -screwspacey / 2, -fudge]) {
        cylinder(d = screwdiam, h = camheight, center = false, $fn =360);
    }
    translate([-screwspacex / 2, screwspacey / 2, -fudge]) {
        cylinder(d = screwdiam, h = camheight, center = false, $fn =360);
    }
    translate([screwspacex / 2, screwspacey / 2, -fudge]) {
        cylinder(d = screwdiam, h = camheight, center = false, $fn =360);
    }
    translate([-screwspacex / 2, -screwspacey / 2, platedepth + 2 - fudge]) {
        cylinder(d = screwdiam + 2 * rimwidth, h = camheight, center = false, $fn =360);
    }
    translate([screwspacex / 2, -screwspacey / 2, platedepth + 2 - fudge]) {
        cylinder(d = screwdiam + 2 * rimwidth, h = camheight, center = false, $fn =360);
    }
    translate([-screwspacex / 2, screwspacey / 2, platedepth + 2 - fudge]) {
        cylinder(d = screwdiam + 2 * rimwidth, h = camheight, center = false, $fn =360);
    }
    translate([screwspacex / 2, screwspacey / 2, platedepth + 2 - fudge]) {
        cylinder(d = screwdiam + 2 * rimwidth, h = camheight, center = false, $fn =360);
    }
}

