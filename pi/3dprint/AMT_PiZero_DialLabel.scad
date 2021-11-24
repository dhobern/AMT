use <allerta.stencil.ttf>

fudge = 0.1;
fudge2 = 0.2;
thickness = 2;
cut = thickness + fudge2;
$fn = 360;
width = 66;
height = 40;
bevel= 2;


difference() {
    translate([-5, -6, 0]) {
        polyhedron(points = [[0, 0, 0], [width, 0, 0], [width, height, 0], [0, height, 0], [bevel, bevel, thickness], [width - bevel, bevel, thickness], [width - bevel, height - bevel, thickness], [bevel, height - bevel, thickness]], faces = [[0,1,2,3],[4,5,1,0],[7,6,5,4],[5,6,2,1],[6,7,3,2],[7,4,0,3]],  convexity = 10);
    }
    translate([0, 0, -fudge]) {
        translate([-14, -6, 0]) cube([14, 23.5, cut]);
        translate([-14, -6, 0]) cube([31.5, 5.5, cut]);
        cylinder(d = 35, h = cut);
        for (i = [0, 30, 60, 90]) {
            rotate([0, 0, -i]) {
                translate([-1, 19, 0]) cube([2, 4, cut]);
            }
        }
        translate([-2, 25, 0]) linear_extrude(height = cut) text("Automatic", font = "Allerta", size = 6);
        translate([14, 16, 0]) linear_extrude(height = cut) text("Manual", font = "Allerta", size = 6);
        translate([22, 7, 0]) linear_extrude(height = cut) text("Transfer", font = "Allerta", size = 6);
        translate([25, -3, 0]) linear_extrude(height = cut) text("Off", font = "Allerta", size = 6);
        translate([44.5, 17.5, 0]) difference() {
            cube([18, 18, cut]);
            translate([0, 0, -fudge]) cylinder(d1 = 33 + 2 * fudge, d2 = 33 - 2 * bevel, h = cut + fudge2);
        }
    }
}