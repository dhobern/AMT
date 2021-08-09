diam1 = 30;
diam2 = 18;

length = 15.3;
width = 9.5;
depth = 13;

fudge = 0.1;
fudge2 = fudge *2;

difference() {
   cylinder(d1 = diam1, d2 = diam2, h = depth, center = false, $fn = 360);
    
    translate([(-length + width) / 2, 0, -fudge]) {
        cylinder(d = width, h = depth + fudge2, center = false, $fn = 360);
    }

    translate([(length - width) / 2, 0, -fudge]) {
        cylinder(d = width, h = depth + fudge2, center = false, $fn = 360);
    }

    translate([(-length + width) / 2, -width / 2, -fudge]) {
        cube([length - width, width, depth + fudge2]);
    }
}

