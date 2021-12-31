lensdiam = 31;
fieldangle = 45;
outerangle = 40;
shielddepth = 60;
outerdiam = lensdiam + (shielddepth * tan(fieldangle));
innerdiam = outerdiam - (shielddepth / tan(outerangle));
diam = 80;
thickness = 2;
innerdepth = 5;

outerheight = ((diam / 2) - thickness) / tan(fieldangle);
angle = atan(outerheight/diam);

screwdiam = 3.5;
screwdepth = 8;

fudge = 0.1;
fudge2 = 0.2;
fudge3 = 0.3;

$fn = 360;

difference() {
    union() {
        difference() {
            union() {
                cylinder(d = diam, h = shielddepth, center = false, $fn=360);
                translate([0, diam / 4 + thickness, 17.5]) {
                    cylinder(d = diam / 2, h = shielddepth - 15);
                }
            }

            translate([0, 0, thickness]) {
                cylinder(d = diam - 2 * thickness, h = shielddepth, center = false, $fn=360);
            }
            translate([0, 0, -fudge]) {
                cylinder(d1 = lensdiam, h = thickness + fudge2, center = false, $fn=360);
            }
            translate([-diam/2 - fudge, -diam/2 - fudge, 0]) rotate([angle, 0, 0]) {
                cube([diam + fudge2, diam * 2 + fudge2, outerdiam + fudge2]);  
            }
        }

        cylinder(d = diam, h = thickness, center = false, $fn=360);
    }
    
    translate([0, 0, -fudge]) {
        cylinder(d = lensdiam, h = thickness + fudge2, center = false, $fn=360);
    }
    for (i = [-lensdiam / 2 - 5, lensdiam / 2 + 5]) {
        translate([i, 0, -fudge]) {
            cylinder(d = screwdiam, h = screwdepth + fudge, center = false);
        }
        translate([0, i, -fudge]) {
            cylinder(d = screwdiam, h = screwdepth + fudge, center = false);
        }
    }
}

/*
translate([diam + 5, 0, 0]) {
    difference() {
        cylinder(d = lensdiam + 20, h = thickness, center = false);
        translate([0, 0, -fudge]) {
            cylinder(d = lensdiam, h = thickness + fudge2, center = false);
        }
        for (i = [-lensdiam / 2 - 5, lensdiam / 2 + 5]) {
            translate([i, 0, -fudge]) {
                cylinder(d = screwdiam, h = thickness + fudge2, center = false);
            }
            translate([0, i, -fudge]) {
                cylinder(d = screwdiam, h = thickness + fudge2, center = false);
            }
        }
    }
}
*/
