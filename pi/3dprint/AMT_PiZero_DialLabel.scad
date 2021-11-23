fudge = 0.1;
fudge2 = 0.2;
thickness = 1;
cut = thickness + fudge2;
$fn = 360;

difference() {
    translate([-13, -5, 0]) cube([60, 36, 1]);
    translate([0, 0, -fudge]) {
        translate([-14, -6, 0]) cube([14, 23.5, cut]);
        translate([-14, -6, 0]) cube([31.5, 5.5, cut]);
        cylinder(d = 35, h = cut);
        for (i = [0, 30, 60, 90]) {
            rotate([0, 0, -i]) {
                translate([-0.5, 19, 0]) cube([1, 4, cut]);
            }
        }
        translate([-9, 25, 0]) linear_extrude(height = thickness + fudge2) text("Automatic", size = 3);
        translate([13, 21, 0]) linear_extrude(height = thickness + fudge2) text("Manual", size = 3);
        translate([22, 11, 0]) linear_extrude(height = thickness + fudge2) text("Transfer", size = 3);
        translate([25, -1, 0]) linear_extrude(height = thickness + fudge2) text("Shutdown", size = 3);
        translate([29.5, 13.5, 0]) difference() {
            cube([18, 18, cut]);
            translate([0, 0, -fudge]) cylinder(d = 35, h = cut + fudge2);
        }
    }
}