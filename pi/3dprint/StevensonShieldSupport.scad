$fn = 360;
fudge = 0.1;
fudge2 = 2 * fudge;

diam = 19.8;
roddiam = 12;
basediam = 40;
baseheight = 10;
height = 50;
channeldiam = 5;

difference() {
    union() {
        cylinder(d = basediam, h = baseheight);
        cylinder(d = diam, h = height);
    }
    translate([0,0,-fudge]) {
        cylinder(d = roddiam, h = height + fudge2);
    }
    translate([(diam + basediam)/4,0,-fudge]) {
        cylinder(d = channeldiam, h = baseheight + fudge2);
    }
}