use <allerta.stencil.ttf>

fudge = 0.1;
fudge2 = 0.2;
thickness = 2.4;
cut = thickness + fudge2;
$fn = 360;

width = 106;
height = 36;
bevel = 2;

difference() {
    polyhedron(points = [[0, 0, 0], [width, 0, 0], [width, height, 0], [0, height, 0], [bevel, bevel, thickness], [width - bevel, bevel, thickness], [width - bevel, height - bevel, thickness], [bevel, height - bevel, thickness]], faces = [[0,1,2,3],[4,5,1,0],[7,6,5,4],[5,6,2,1],[6,7,3,2],[7,4,0,3]],  convexity = 10);
    
    translate([width / 2, height - 9, 0.4]) linear_extrude(height = cut) text("Autonomous Moth Trap", font = ":style=Bold", size = 6, halign = "center");
    translate([width / 2, height - 17, 0.4]) linear_extrude(height = cut) text("https://amt.hobern.net/", font = ":style=Bold", size = 6, halign = "center");
    translate([width / 2, height - 25, 0.4]) linear_extrude(height = cut) text("Contact: Donald Hobern", font = ":style=Bold", size = 6, halign = "center");
    translate([width / 2, height - 33, 0.4]) linear_extrude(height = cut) text("Phone: AU 0420511471", font = ":style=Bold", size = 6, halign = "center");
}