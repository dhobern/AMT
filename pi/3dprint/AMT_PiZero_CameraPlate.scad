thickness = 3;
riserthickness = 2;

fudge = 0.1;
fudge2 = 0.2;
fudge3 = 0.3;

margin = 3;

camerascrewgap = 30;
basescrewgap = 45;
cameradiam = 35;
lensdiam = 31;
piscrewdiam = 2.9;
holedepth = 8;

screwdiam = 3.3;

rise = 30;

$fn = 360;

width = basescrewgap + screwdiam + 2 * margin;
length = width / 2;
basescrewinset = (width - basescrewgap) / 2;
camerascrewinset = (width - camerascrewgap) / 2;

for(p = [0, length + thickness]) translate([0, p, 0]) {
    difference() {
        union() {
            cube([width, length, thickness]);
            for(i = [basescrewinset, width - basescrewinset]) {
                translate([i, basescrewinset, 0]) {
                    cylinder(d = piscrewdiam + 2 * margin, h = thickness + rise);
                }
            } 
        }
        translate([width / 2, length, -fudge]) {
            cylinder(d = cameradiam, h = thickness + fudge2);
        }
        for(i = [basescrewinset, width - basescrewinset]) {
            translate([i, basescrewinset, thickness + rise - holedepth]) {
                cylinder(d = screwdiam, h = holedepth + fudge);
            }
        } 
        for(i = [camerascrewinset, width - camerascrewinset]) {
            translate([i, camerascrewinset, -fudge]) {
                cylinder(d = piscrewdiam, h = thickness + fudge2);
            }
        } 
    }
}