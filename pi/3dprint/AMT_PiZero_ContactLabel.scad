use <allerta.stencil.ttf>

fudge = 0.1;
fudge2 = 0.2;
thickness = 2;
cut = thickness + fudge2;
$fn = 360;

width = 106;
height = 35;
bevel = 2;

difference() {
    polyhedron(points = [[0, 0, 0], [width, 0, 0], [width, height, 0], [0, height, 0], [bevel, bevel, thickness], [width - bevel, bevel, thickness], [width - bevel, height - bevel, thickness], [bevel, height - bevel, thickness]], faces = [[0,1,2,3],[4,5,1,0],[7,6,5,4],[5,6,2,1],[6,7,3,2],[7,4,0,3]],  convexity = 10);
    
    translate([width / 2, height - 10, -fudge]) linear_extrude(height = cut) text("Autonomous Moth Trap", font = "Allerta", size = 6, halign = "center");
    translate([width / 2, height - 21, -fudge]) linear_extrude(height = cut) text("https://amt.hobern.net/", font = "Allerta", size = 5, halign = "center");
    translate([width / 2, height - 31, -fudge]) linear_extrude(height = cut) text("Donald Hobern - 0420511471", font = "Allerta", size = 5, halign = "center");
}