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
toothh = 7.5;

width = spacing + bumpdiam + 2 * margin;
height = footh + clearance + plate + bumpinset + bumpdiam + margin;
fudge = 0.1;
fudge2 = 2 * fudge;

difference() {
    union() {
        cube([width, plate + bumph, height - 1]);

        for(i = [0, width - bumpdiam - 2 * margin]) {
            translate([i, -footl, 0]) {
                cube([bumpdiam + 2 * margin, footl + fudge, footh]);
            } 
            translate([i, -clearance, 0]) {
                cube([bumpdiam + 2 * margin, clearance + plate + bumph + ledgel, footh + clearance]);
            }
            translate([i, 0, footh + clearance]) {
                cube([bumpdiam + 2 * margin, plate + bumph + ledgel, plate]);
            }
            translate([i, 0, 0]) {
                cube([bumpdiam + 2 * margin, footl + plate + bumph + ledgel, footh]);
            } 
        }
    }

    translate([bumpdiam + 2 * margin + footh +  clearance, -fudge, -fudge]) {
        cube([width - 2 * bumpdiam - 4 * margin - 2 * footh - 2 * clearance, bumph + plate + fudge2, footh + clearance + fudge]);
    }
    for(i = [bumpdiam + 2 * margin + footh + clearance, width - bumpdiam - 2 * margin - footh - clearance]) {
        translate([i, -fudge, 0]) {
            rotate([-90, 0, 0]) {
                cylinder(r = footh + clearance, h = bumph + plate + fudge2, center = false, $fn = 360);
            }
        }
    } 
    
    translate([(width - innerwidth) / 2, -fudge, footh + clearance + plate + margin + 8]) {
        cube([innerwidth, plate + bumph + fudge2, bumpinset + bumpdiam + margin - margin + fudge + 8]);
    }
    
    translate([-fudge, -clearance, footh + clearance]) {
        rotate([0, 90, 0]) {
            cylinder(d = 2 * clearance, h = width + fudge2, center = false, $fn = 360);
        }
    }
    
    translate([-fudge, plate + bumph + ledgel - toothd, footh + clearance - toothh]) {
        cube([width + fudge2, toothd + fudge, toothw]);
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

    for(i = [8.9, 128.1]) {
        translate([i, plate + bumph + ledgel - toothd, footh + clearance + plate - toothh]) {
            cube([toothw, toothd + fudge, toothh + fudge]);
        }
    }
}