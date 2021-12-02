outerdiam = 70;
innerdiam = 50;
height = 20;
nesting = 5;
rod = 11.5;
thickness = 2;
totalheight = 100;
cable = 6;
sensorx = 10;
sensory = 18;
screw = 3.5;
screwinset = 6.5;

fudge = 0.1;
fudge2 = 0.2;
fudge3 = 0.3;
$fn = 360;

difference() {
    union() {
        difference() {
            cylinder(d1 = innerdiam, d2 = outerdiam, h = height);
            translate([0, 0, thickness + fudge]) {
                cylinder(d1 = innerdiam - 2 * thickness, d2 = outerdiam - 2 * thickness, h = height - thickness);
            }
        }
        cylinder(d = rod + 4 * thickness, h = height - nesting);
    }
    translate([0, 0, -fudge]) {
        cylinder(d = rod + 2 * thickness + fudge3, h = height);
    }
    for (j = [rod / 2 + 2 * thickness + cable / 2, -rod / 2 - 2 * thickness - cable / 2]) {
        translate([0, j, -fudge]) {
            cylinder(d = cable, h = thickness + fudge3);
        }
    }
    for (j = [rod / 2 + 2 * thickness + fudge, -(rod /2 + 2 * thickness + fudge)  - sensorx]) {
        translate([j, -sensory / 2, -fudge]) {
            cube([sensorx, sensory, thickness + fudge3]);
            for (i = [0, sensory]) {
                translate([sensorx / 2, i]) {
                    cylinder(d = sensorx, h = thickness + fudge3);
                }
            }
        }
    }
}