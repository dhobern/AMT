screwx = 115;
screwy = 182;

margin = 2;

screwdiam = 3.1;

rise = 4.5;

thickness = 3;

fudge = 0.1;
fudge2 = 0.2;
fudge3 = 0.3;

x = screwx + screwdiam + 2 * margin;
y = screwy + screwdiam + 2 * margin;

$fn = 360;

difference() {
    union() {
        cube([x, screwdiam + 2 * margin, 0.8]);
        cube([screwdiam + 2 * margin, y, 0.8]);
    }
    
    for (i = [margin + screwdiam / 2, x - margin - screwdiam / 2]) {
        for (j = [margin + screwdiam / 2, y - margin - screwdiam / 2]) {
            translate([i, j, -fudge]) {
                cylinder(d = screwdiam, h = 1);
            }
        }
    }
}
