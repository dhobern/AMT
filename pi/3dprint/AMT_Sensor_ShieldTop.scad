outerdiam = 70;
innerdiam = 50;
height = 20;
nesting = 5;
rod = 11.5;
thickness = 2;
totalheight = 100;
cable = 5;
sensorx = 10;
sensory = 20;
screw = 3.5;
screwinset = 6.5;

fudge = 0.1;
fudge2 = 0.2;
fudge3 = 0.3;
$fn = 360;

union() {
    difference() {
        cylinder(d1 = innerdiam, d2 = outerdiam, h = height);
        translate([0, 0, thickness + fudge]) {
            cylinder(d1 = innerdiam - 2 * thickness, d2 = outerdiam - 2 * thickness, h = height - thickness);
        }
    }
    difference() {
        union() {
            cylinder(d = rod + 2 * thickness - fudge3, h = totalheight);
            cylinder(d = rod + 4 * thickness, h = height - nesting);
        }
        translate([0, 0, thickness]) {
            cylinder(d = rod, h = totalheight);
        }
        translate([0, -rod / 2 - thickness - fudge, totalheight - screwinset]) {
            rotate([-90, 0, 0,]) {
                cylinder(d = screw, h = rod + 2 * thickness + fudge2);
            }
        }
    }
}
