yspacing = 25;
xspacing = 110;

boltx = 83;
bolty = 65;

powerdepth = 32;
powerheight = 30;
powerspacing = 70;

rimwidth = 3;
screwdiam = 4;
boltdiam = 3;
platedepth = 4;

fudge = 0.1;
fudge2 = 2 * fudge;

width = xspacing + 2 * rimwidth + screwdiam;
length = 3 * yspacing + 2 * rimwidth + screwdiam;

boardwidth = boltx + 2 * rimwidth + boltdiam;
boardlength = bolty + 2 * rimwidth + boltdiam;
clearance = 5;

xoffset = width - boltx;
yoffset = (length - bolty) / 2;
zoffset = platedepth + clearance;

screwoffset = rimwidth + screwdiam / 2;

difference() {
    union() {
        translate([-boltdiam / 2 - rimwidth, -boltdiam / 2 - rimwidth, 0]) {
            cube([width + boltdiam + 2 + rimwidth, length + boltdiam + 2 + rimwidth, platedepth]);
        }
        translate([powerspacing - boltdiam / 2 - 2 * rimwidth, -boltdiam / 2 - 2 * rimwidth, 0]) {
            cube([boltdiam + 4 * rimwidth, length + boltdiam + 4 * rimwidth, platedepth]);
        }
        for (i = [xoffset, xoffset + boltx]) {
            for (j = [yoffset, yoffset + bolty]) {
                translate([i, j, 0]) {
                    cylinder(d = boltdiam + 2 * rimwidth, h = zoffset, center = false, $fn = 360);
                }
            }
        }
        for(i = [0, powerspacing]) {
            for(j = [0, length]) { 
                translate([i, j, 0]) {
                    cylinder(d = boltdiam + 2 * rimwidth, h = powerheight + platedepth, center = false, $fn = 360);
                }
            }
        }
    }
    for (i = [screwoffset, width - screwoffset]) {
        for (j = [screwoffset, length - screwoffset]) {
            translate([i, j, -fudge]) {
                cylinder(d = screwdiam, h = platedepth + fudge2, center = false, $fn =360);
            }
        }
    }
    for (i = [xoffset, xoffset + boltx]) {
        for (j = [yoffset, yoffset + bolty]) {
            translate([i, j, platedepth]) {
                cylinder(d = boltdiam, h = clearance + fudge, center = false, $fn = 360);
            }
        }
    }
        for(i = [0, 70]) {
            for(j = [0, length]) { 
            translate([i, j, platedepth]) {
                cylinder(d = boltdiam, h = powerheight + fudge, center = false, $fn = 360);
            }
        }
    }
    translate([boltdiam + 3 * rimwidth, boltdiam + 2 * rimwidth, -fudge]) {
        cube([xoffset - (3 * boltdiam) / 2 - 5 * rimwidth, length - 2 * boltdiam - 4 * rimwidth, platedepth + fudge2]);
    }
    translate([xoffset + boltdiam / 2 + 2 * rimwidth, boltdiam + 2 * rimwidth, -fudge]) {
        cube([powerspacing - xoffset - (3 * boltdiam) / 2 - 4 * rimwidth, length - 2 * boltdiam - 4 * rimwidth, platedepth + fudge2]);
    }
    translate([70 + boltdiam / 2 + 2 * rimwidth, boltdiam + 2 * rimwidth, -fudge]) {
        cube([width - powerspacing - (3 * boltdiam) / 2 - 5 * rimwidth, length - 2 * boltdiam - 4 * rimwidth, platedepth + fudge2]);
    }
}