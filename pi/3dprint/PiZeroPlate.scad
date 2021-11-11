$fn = 360;

fudge = 0.1;
fudge2 = fudge * 2;

screww = 90;
screwl = 132.5;
screwd = 3.2;
headspacew = 70;
headspacel = 10;

margin = 3;
thickness = 3;
offset = 5;

cameralength = 40;
cameraspacing = 30;
camerasize = 38;
cameradiam = 35;
camerasplit = 1;
cameraadjust = 5;

zerow = 58;
zerol = 23;

circuitw = 83;
circuitl = 65;

w = screww + screwd + 2 * margin;
l = screwl + screwd + 2 * margin;

cw = camerasize + 4 * margin + 2 * screwd;
cl = cw;

inset = margin + screwd/2;

pillarheight = cameralength - offset - thickness;

circuitoffsetl = l + headspacel - cl - circuitl - 2 * margin;

lensdiam = 30.5;
lensdiskdiam = lensdiam + 20;

difference() {
    union() {
        cube([w, l, thickness]);
        translate([(w - headspacew) / 2, -headspacel, 0]) {
            cube([headspacew, l + 2 * headspacel, thickness]);
        }
        for (i = [-headspacel, l + headspacel - cl, l + headspacel - 2 * inset]) {
            translate([(w - cw) / 2 + 2 * inset, i, 0]) {
                cube([cw - 4 * inset, 2 * inset, thickness + offset]);
            }
        }
    }
    for (i = [inset, w - inset]) {
        for (j = [inset, l - inset]) {
            translate([i, j, -fudge]) {
                cylinder(d = screwd, h = thickness + fudge2);
            }
        }
    }
    translate([w / 2, l + headspacel - cl/2, -fudge]) {
        cylinder(d = cameradiam + 2 * cameraadjust, h = thickness + fudge2);
    }
    translate([w / 2, l + headspacel - cl/2, thickness]) {
        cylinder(d = lensdiskdiam + 2 * fudge2, h = offset + fudge);
    }
    translate([(w - cw) / 2, l + headspacel - cl, 0]) {
        for (i = [inset, cw - inset]) {
            for (j = [inset, cl - inset]) {
                translate([i, j, -fudge]) {
                    cylinder(d = screwd, h = thickness + fudge2);
                }
            }
        }
    }
    for(i = [(w - circuitw) / 2, (w + circuitw) / 2]) {
        for(j = [0, circuitl]) {
            translate([i, circuitoffsetl + j, -fudge]) {
                cylinder(d = screwd, h = thickness + fudge2);
            }
        }
    }
    for(i = [(w - zerow) / 2, (w + zerow) / 2]) {
        for(j = [0, zerol]) {
            translate([i, j -headspacel + inset, -fudge]) {
                cylinder(d = screwd, h = thickness + fudge2);
            }
        }
    }
    translate([(w - circuitw) / 2 + inset, circuitoffsetl + inset, -fudge]) {
        cube([circuitw - 2 * inset, circuitl - 2 * inset, thickness + fudge2]);
    }
    translate([(w - zerow) / 2 + inset, 2 * inset - headspacel, -fudge]) {
        cube([zerow - 2 * inset, zerol - 2 * inset, thickness + fudge2]);
    }
}

translate([w + margin, 0, 0]) difference() {
    difference() {
        union() {
            cube([cw, cl, thickness]);
            for (i = [inset, cw - inset]) {
                for (j = [inset, cl - inset]) {
                    translate([i, j, 0]) {
                        cylinder(d = screwd + 2 * margin, h = pillarheight);
                    }
                }
            }
        }
        translate([cw / 2, cl / 2, -fudge]) {
            cylinder(d = cameradiam, h = thickness + fudge2);
        }
        for (i = [(cw - cameraspacing) / 2, (cw + cameraspacing) / 2]) {
            for (j = [(cl - cameraspacing) / 2, (cl + cameraspacing) / 2]) {
                translate([i, j, -fudge]) {
                    cylinder(d = screwd, h = thickness + fudge2);
                }
            }
        }
        for (i = [inset, cw - inset]) {
            for (j = [inset, cl - inset]) {
                translate([i, j, pillarheight - 8]) {
                    cylinder(d = screwd, h = pillarheight - 8 + fudge);
                }
            }
        }
        translate([(cw - camerasplit) / 2, -fudge, -fudge]) {
           cube([camerasplit, cl + fudge2, thickness + fudge2]); 
        }
    }
}