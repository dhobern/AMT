spacing = 12;
depth = 7;
thickness = 2;
length = 10;
width = 19;
screwdiam = 3.2;
radius = 4;

fudge = 0.1;
fudge2 = 2 * fudge;

difference() {
    cube([width, length, depth]);
    
    translate([(width - spacing) / 2 + thickness, -fudge, thickness]) {
        cube([spacing - (thickness  * 2), length + fudge2, depth]);
    }
    translate([0, -fudge, thickness]) rotate([-90, 0, 0]) {
        cylinder(r = radius, h = length + fudge2, center = false, $fn = 360);
    }
    translate([width, -fudge, thickness]) rotate([-90, 0, 0]) {
        cylinder(r = radius, h = length + fudge2, center = false, $fn = 360);
    }
    translate([width / 2, length / 2, -fudge]) {
        cylinder(d = screwdiam, h = depth, center = false, $fn = 360);
    }
} 