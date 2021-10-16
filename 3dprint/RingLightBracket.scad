projl = 15;
projw = 50;
projd = 6;

boltd = 6;
bolthd = 12.5;
bolthh = 4.5;

basew = projw;
baseh = 16;
basel = 30;

fudge = 0.1;
fudge2 = fudge * 2;

screwd = 3.5;
screwhd = 6;
screwsw = 30;

coverw = 24;
coverl = 20;
coverd = 6;
coverh = 41;
flanged = 3;

translate([coverw + 5, basel, baseh]) {
    rotate([180, 0, 0]) {
        difference() {
            union() {
                cube([basew, basel, baseh]);
                translate([0, -projl, baseh - projd]) {
                    difference() {
                        cube([projw, projl + basel, projd]);
                        translate([projw / 2, projl / 2, -fudge]) {
                            cylinder(d = boltd, h = projd + fudge2, center = false, $fn = 360);
                            cylinder(d1 = bolthd, d2 = boltd, h = bolthh, center = false, $fn = 360);
                        }
                    }
                }
            }
            
            for (i = [(basew - screwsw) / 2, basew - (basew - screwsw) / 2]) {
                translate([i, basel / 3, -fudge]) {
                    cylinder(d = screwd, h = baseh - 3, center = false, $fn = 360);
                }
            } 
            translate([basew / 2, basel * 2 / 3, -fudge]) {
                cylinder(d = screwd, h = baseh - 3, center = false, $fn = 360);
            }
            for (i = [5, basew - 5]) {
                for (j = [5, basel - 5]) {
                    translate([i, j, fudge + 3]) {
                        cylinder(d = screwd, h = baseh - 3, center = false, $fn = 360);
                    }
                }
            }
        }
    }
}

translate([coverw + basew + 10, 0, 0]) {
    difference() {
        union() {
            cube([basew, basel, flanged]);
            translate([(basew - coverw) / 2, 0, 0]) {
                cube([coverw, coverl, coverh]);
            }
        }
        
        for (i = [5, basew - 5]) {
            for (j = [5, basel - 5]) {
                translate([i, j, -fudge]) {
                    cylinder(d = screwd, h = flanged + fudge2, center = false, $fn = 360);
                }
            }
        }
        for (i = [(basew - coverw) / 2 + 5, basew - (basew - coverw) / 2 - 5]) {
            translate([i, coverl / 2, 3]) {
                cylinder(d = screwd, h = coverh + fudge2, center = false, $fn = 360);
            }
        }
    }
}

difference() {
    cube([coverw, projl + coverl, projd]);
    translate([coverw / 2, projl / 2, -fudge]) {
        cylinder(d = boltd, h = projd + fudge2, center = false, $fn = 360);
        translate([0, 0, projd - bolthh + fudge2]) {
            cylinder(d1 = boltd, d2 = bolthd, h = bolthh, center = false, $fn = 360);
        }
    }
    for (i = [5, coverw - 5]) {
        translate([i, projl + coverl / 2, -fudge]) {
            cylinder(d = screwd, h = projd + fudge2, center = false, $fn = 360);
            translate([0, 0, 3]) {
                cylinder(d = screwhd, h = projd + fudge2, center = false, $fn = 360);
            }
        }
    }
}
