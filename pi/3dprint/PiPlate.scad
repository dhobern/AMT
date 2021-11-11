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
camwidth = 27.2;

wall = 2;

platedepth = 3;
platex = camlength + (4 * wall);
platey = camwidth + (2 * wall);

pegheight = 7;

columndiam = 8;

upperspacingx = camlength * 2 / 3;
upperspacingy = platey + columndiam - (2 * wall);

lowerspacing = 50;

f2bspacing = 55 - (upperspacingy / 2) + (screwspacey / 2);

difference() {
    union() {
        cube([upperspacingx + screwdiam + 2 * rimwidth, f2bspacing + screwdiam + 2 * rimwidth, platedepth]);
        translate([0, -upperspacingy, 0]) {
            cube([screwdiam + 2 * rimwidth, upperspacingy + fudge, platedepth]);
        }
        translate([upperspacingx, -upperspacingy, 0]) {
            cube([screwdiam + 2 * rimwidth, upperspacingy + fudge, platedepth]);
        }
        translate([(upperspacingx + screwdiam) / 2 + rimwidth - lowerspacing / 2, f2bspacing + rimwidth + (screwdiam / 2), 0]) {
            cylinder(d = screwdiam + rimwidth * 2, h = platedepth + camheight - pegheight, center = false, $fn = 360);
            cylinder(d = screwdiam - 1, h = platedepth + camheight - (pegheight / 2), center = false, $fn = 360);
        }
        translate([(upperspacingx + screwdiam) / 2 + rimwidth + lowerspacing / 2, f2bspacing + rimwidth + (screwdiam / 2), 0]) {
            cylinder(d = screwdiam + rimwidth * 2, h = platedepth + camheight - pegheight, center = false, $fn = 360);
            cylinder(d = screwdiam - 1, h = platedepth + camheight - (pegheight / 2), center = false, $fn = 360);
            
        }
    }

    translate([screwdiam + 3 * rimwidth, 4 * rimwidth, -fudge]) {
        cube([upperspacingx - screwdiam - 4 * rimwidth, (4 * rimwidth), platedepth + fudge2]);
    }
    
    translate([screwdiam + 3 * rimwidth, f2bspacing + screwdiam + 2 * rimwidth - (8 * rimwidth), -fudge]) {
        cube([upperspacingx - screwdiam - 4 * rimwidth, (4 * rimwidth), platedepth + fudge2]);
    }

    translate([rimwidth + screwdiam / 2, rimwidth + screwdiam / 2, -fudge]) {
        cylinder(d = screwdiam, h = platedepth + fudge2, center = false, $fn = 360);
    }
    translate([upperspacingx + rimwidth + screwdiam / 2, rimwidth + screwdiam / 2, -fudge]) {
        cylinder(d = screwdiam, h = platedepth + fudge2, center = false, $fn = 360);
    }
    translate([rimwidth + screwdiam / 2, rimwidth + screwdiam / 2 - upperspacingy, -fudge]) {
        cylinder(d = screwdiam, h = platedepth + fudge2, center = false, $fn = 360);
    }
    translate([upperspacingx + rimwidth + screwdiam / 2, rimwidth + screwdiam / 2 - upperspacingy, -fudge]) {
        cylinder(d = screwdiam, h = platedepth + fudge2, center = false, $fn = 360);
    }
}
