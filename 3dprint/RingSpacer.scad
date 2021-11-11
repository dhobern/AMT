shielddiam = 80;
ringdiam = 110;
thickness = 2;
ringthickness = 18;
fudge = 0.1;
fudge2 = 2 * fudge;

$fn = 360;

difference() {
    cylinder(d = ringdiam, h = ringthickness);
    translate([0,0,-fudge]) {
        cylinder(d = shielddiam + fudge2, h = ringthickness + fudge2);
    }
}
        