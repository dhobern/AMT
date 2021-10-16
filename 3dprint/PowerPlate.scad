yspacing = 25;
xspacing = 110;

powerdepth = 32;
powerwidth = 56;
powerspacing = 70;
xoverhang = 30;

rimwidth = 3;
screwdiam = 4;
boltdiam = 3;
platedepth = 3;

boltspacing = rimwidth + boltdiam / 2;

fudge = 0.1;
fudge2 = 2 * fudge;

width = powerspacing + 2 * rimwidth + screwdiam + xoverhang;
length = 3 * yspacing + 4 * rimwidth + screwdiam + boltdiam;

difference() {
    cube([width, length, platedepth]);
    translate([22, 15, -fudge]) {
        cube([width - 44, length - 30, platedepth + fudge2]);
        }
    for(i = [boltspacing, powerspacing + boltspacing]) {
        for(j = [ boltspacing, length - boltspacing]) {
            translate([i, j, -fudge]) {
                cylinder(d = screwdiam, h = platedepth + fudge2, center = false, $fn = 360);
            }
        }
    }       
}
translate([48, 2 + rimwidth + boltdiam / 2, 0]) {
    rotate([0, 0, 45]) {
        for(i = [0, powerwidth + boltdiam + 2 * rimwidth]) {
            for(j = [0, 45]) {
                translate([i, j, 0]) {
                    difference() {
                        cylinder(d = boltdiam + 2 * rimwidth, h = powerdepth + platedepth, center = false, $fn = 360);
                        translate([0, 0, platedepth]) {
                            cylinder(d = boltdiam, h = powerdepth + fudge, center =  false, $fn = 360);
                        }
                    }
                }
            }
        }
    }
}

translate([20, -60, 0]) {
    difference() {
        cube([powerwidth + boltdiam * 2 + rimwidth * 4,
              45 + boltdiam + rimwidth * 2, platedepth]);
        translate([boltdiam + 2 * rimwidth, boltdiam + 2 * rimwidth, -fudge]) {
            cube([powerwidth, 45 - boltdiam - 2 * rimwidth, platedepth + fudge2]);
        }
        for(i = [0, powerwidth + boltdiam + 2 * rimwidth]) {
            for(j = [0, 45]) {
                translate([i + rimwidth + boltdiam / 2, j + rimwidth + boltdiam / 2, -fudge]) {
                    cylinder(d = screwdiam, h = platedepth + fudge2, center =  false, $fn = 360);
                }
            }
        }
    }
}
