spacing = 120;
innerwidth = 60;
bumpdiam = 10.2;
bumph = 2;
bumpinset = 7.5;
screwdiam = 3.6;
footscrewdiam = 4;
plate = 3;
margin = 5;
clearance = 11;
footh = 5;
footl = 40;
ledgel = 61.5;
toothd = 4;
toothw = 3;

width = spacing + bumpdiam + 2 * margin;
height = footh + clearance + plate + bumpinset + bumpdiam + margin;
fudge = 0.1;
fudge2 = 2 * fudge;

difference() {
    union() {
        cube([width, plate + bumph, height]);

        for(i = [0, width - bumpdiam - 2 * margin]) {
            translate([i, -footl, 0]) {
                cube([bumpdiam + 2 * margin, footl + fudge, footh]);
            } 
            translate([i, -clearance, 0]) {
                cube([bumpdiam + 2 * margin, clearance + plate + bumph + ledgel, footh + clearance + plate]);
            }
            translate([i, 0, 0]) {
                cube([bumpdiam + 2 * margin, footl + plate + bumph + ledgel, footh]);
            } 
        }
    }
    
    translate([(width - innerwidth) / 2, -fudge, footh + clearance + plate + margin]) {
        cube([innerwidth, plate + bumph + fudge2, bumpinset + bumpdiam + margin - margin + fudge]);
    }
    
    translate([-fudge, -clearance, footh + clearance]) {
        rotate([0, 90, 0]) {
            cylinder(d = 2 * clearance, h = width + fudge2, center = false, $fn = 360);
        }
    }
    
    translate([-fudge, plate + bumph + ledgel, footh + (clearance) / 2]) {
        rotate([0, 90, 0]) {
            cylinder(d = clearance, h = width + fudge2, center = false, $fn = 360);
        }
    }
    
    for(i = [margin + bumpdiam / 2, width - margin - bumpdiam / 2]) {
        translate([i, -fudge, height - margin - bumpdiam / 2]) {
            rotate([-90, 0, 0]) {
                cylinder(d = screwdiam, h = plate + bumph + fudge2, center = false, $fn = 360);
                translate([0, 0, plate]) {
                    cylinder(d = bumpdiam, h = bumph + fudge2, center = false, $fn = 360);
                }
            }
        }
        for(j = [-footl + margin + bumpdiam / 2, plate + bumph + ledgel + footl - margin - bumpdiam / 2]) {
            translate([i, j, -fudge]) {
                cylinder(d = footscrewdiam, h = footh + fudge2, center = false, $fn = 360);
            }
        }
        translate([i, -footl + margin + bumpdiam / 2, -fudge]) {
            difference() {
                translate([-margin - bumpdiam / 2 - fudge, -margin - bumpdiam / 2 - fudge, 0]) {
                    cube([margin * 2 + bumpdiam + fudge2, margin + bumpdiam / 2 + fudge, footh + fudge2]);
                }
                translate([0, 0, -fudge2]) {
                    cylinder(d = margin * 2 + bumpdiam, h = footh + 2 * fudge2, center = false, $fn = 360);
                }
            }
        }
    
        translate([i, plate + bumph + ledgel + footl - margin - bumpdiam / 2, -fudge]) {
            difference() {
                translate([-margin - bumpdiam / 2 - fudge, 0, 0]) {
                    cube([margin * 2 + bumpdiam + fudge2, margin + bumpdiam / 2 + fudge, footh + fudge2]);
                }
                translate([0, 0, -fudge2]) {
                    cylinder(d = margin * 2 + bumpdiam, h = footh + 2 * fudge2, center = false, $fn = 360);
                }
            }
        }
    }

    for(i = [8.9, 20.4, 116.6, 128.1]) {
        translate([i, plate + bumph + ledgel - toothd, footh + clearance - plate]) {
            cube([toothw, toothd + fudge, plate * 2 + fudge2]);
        }
    }
}