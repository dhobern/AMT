shielddiam = 80;
outerdiam = 100;
ringdiam = 218;
embedlength = 8;
raylength = (ringdiam - outerdiam) / 2  + embedlength;

pegl = 7.5;
pegw = 3;
pegd = 3;
thickness = 2;
ringthickness = 15;
fudge = 0.1;
fudge2 = 2 * fudge;
rayw = 10;

$fn = 360;

difference() {
    union() {
        cylinder(d = outerdiam + fudge2, h = ringthickness);
    }
    translate([0,0,-fudge]) {
        cylinder(d = shielddiam + fudge2, h = ringthickness + fudge2);
    }
    for (a = [0:8]) {
        rotate([0,0,a * 40]) translate([-(rayw/2) - fudge, outerdiam/2 - embedlength - fudge, ringthickness - thickness - fudge]) {
            cube([rayw + fudge2, raylength + fudge, thickness + fudge2]); 
            translate([(rayw - pegl) /2 - fudge, -fudge, -pegd]) {
                cube([pegl + fudge2, pegw + fudge2, pegd + fudge]);
            }
        }
    }
}


for (a = [0:2]) {
    translate([outerdiam/2 + 5 + a * (rayw + 5), -raylength/2, 0]) {
        cube([rayw, raylength, thickness]); 
        for (i = [0, raylength-pegw]) {
            translate([(rayw - pegl) /2, i, 0]) {
                cube([pegl, pegw, pegd + thickness]);
            }
        }
    }
}
