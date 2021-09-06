boltheight = 19.5;
boltdiam = 6.5;
depth = 8.5;
spacing = 35;
plate = 3;
rim = 3;
screwdiam = 3.5;
offset = 3;

length = spacing + screwdiam + 2 * rim;

fudge = 0.1;
fudge2 = 2 * fudge;

difference() {
    union() {
        cube([length, depth + offset, plate]);
        translate([(length - boltdiam) / 2 - rim, offset, 0]) {
            cube([boltdiam + 2 * rim, depth, boltheight]);
        }
        translate([length / 2, offset, boltheight]) {
            rotate([-90, 0, 0]) {
                cylinder(d = boltdiam + 2 * rim, h = depth, center = false, $fn = 360);
            }
        }
    }
    translate([length / 2, offset - fudge, boltheight]) {
        rotate([-90, 0, 0]) {
            cylinder(d = boltdiam, h = depth + fudge2, center = false, $fn = 360);
        }
    }
    for (i = [rim + screwdiam /2, length - rim - screwdiam / 2]) {
        translate([i, depth / 2, -fudge]) {
            cylinder(d = screwdiam, h = plate + fudge2, center = false, $fn = 360);
        }
    }
}