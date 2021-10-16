length = 79.8;
width = 19.8;
depth = 3;
outerdepth = 1.5;
height = depth + outerdepth;
outerlip = 3;
cornerradius = 4;
wall = 1.75;

leddiam = 5.2;

trimpotwidth = 5.2;
trimpotlength = 6.3;
trimpotheight = 7;
screwdiam = 4;
screwdepth = 1;

switchdiam = 5.0;
switchwidth = 6.0;
switchlength = 9.0;
switchdepth = 7.0;
pushdiam = 3.3;

togglewidth = 5.5;
togglelength = 8;
toggleheight = 7;
togglediam = 5.2;

powerdiam = 16;

ledx = 0.9;
ledy = 0.5;
trimpotx = 0.45;
trimpoty = 0.5;
switchx = 0.75;
switchy = 0.5;
togglex = 0.6;
toggley = 0.5;
powerx = 0.15;
powery = 0.5;
lightx = 0.36;
lighty = 0.5;
tablex = 0.6;
tabley = 0.5;


fudge = 0.1;
fudge2 = fudge * 2;

difference() {
    union() {
        translate([-outerlip + cornerradius,-outerlip,0]) 
            cube([length + (2 * outerlip) - (2 * cornerradius), 
            width + (2 * outerlip), outerdepth]);
        translate([-outerlip,-outerlip + cornerradius,0]) 
            cube([length + (2 * outerlip), 
            width + (2 * outerlip) - (2 * cornerradius)
            , outerdepth]);
        translate([-outerlip + cornerradius, -outerlip + cornerradius, 0])
            cylinder(h = outerdepth, r = cornerradius, center = false, $fn = 360);
        translate([-outerlip + cornerradius, outerlip + width - cornerradius, 0])
            cylinder(h = outerdepth, r = cornerradius, center = false, $fn = 360);
        translate([outerlip + length - cornerradius, -outerlip + cornerradius, 0])
            cylinder(h = outerdepth, r = cornerradius, center = false, $fn = 360);
        translate([outerlip + length - cornerradius, outerlip + width - cornerradius, 0])
            cylinder(h = outerdepth, r = cornerradius, center = false, $fn = 360);    

        translate([0,cornerradius,0]) 
            cube([length, width - 2 * cornerradius, height]);
        translate([cornerradius,0,0]) 
            cube([length - 2 * cornerradius, width, height]);
        translate([cornerradius, cornerradius, 0])
            cylinder(h = height, r = cornerradius, center = false, $fn = 360);
        translate([cornerradius, width -cornerradius, 0])
            cylinder(h = height, r = cornerradius, center = false, $fn = 360);
        translate([length - cornerradius, cornerradius, 0])
            cylinder(h = height, r = cornerradius, center = false, $fn = 360);
        translate([length - cornerradius, width - cornerradius, 0])
            cylinder(h = height, r = cornerradius, center = false, $fn = 360);
            
        translate([(length * switchx) - (switchwidth / 2) - wall, (width * switchy) - (switchlength / 2) - wall, 0])
            cube([switchwidth + (2 * wall), switchlength + (2 * wall), outerdepth + switchdepth]);
            
        translate([(length * trimpotx) - (trimpotwidth / 2) - wall, (width * trimpoty) - trimpotlength + (screwdiam / 2), 0])
            cube([trimpotwidth + (2 * wall), trimpotlength + wall, outerdepth + trimpotheight]);
            
        translate([(length * togglex) - (togglewidth / 2) - wall, (width * toggley) - (togglelength / 2) - wall, 0])
            cube([togglewidth + (2 * wall), togglelength + (2 * wall), outerdepth + toggleheight]);
    }
    
    translate([length * powerx, width * powery , -fudge]) {
        cylinder(d = powerdiam, h = height + fudge2, center = false, $fn =360);
    }
    
    translate([length * ledx, width * ledy , -fudge]) {
        cylinder(d = leddiam, h = height + fudge2, center = false, $fn =360);
    }
    
    translate([length * switchx, width * switchy , -fudge]) {
        cylinder(d = pushdiam, h = height + fudge2, center = false, $fn =360);
        translate([0, 0, depth + fudge]) {
            cylinder(d = switchdiam, h = height + fudge2, center = false, $fn =360);
        }
        translate([-(switchwidth / 2), -(switchlength / 2), height + fudge]) {
            cube([switchwidth, switchlength, outerdepth + switchdepth + fudge2]);
        }
    }

    translate([length * trimpotx, width * trimpoty , -fudge]) {
        cylinder(d = screwdiam, h = height + fudge2, center = false, $fn =360);
        translate([-(trimpotwidth / 2), -trimpotlength + (screwdiam / 2) - fudge, screwdepth + fudge]) {
            cube([trimpotwidth, trimpotlength + fudge, trimpotheight + 1.0 + fudge]);
        }
    }
    
    translate([length * togglex, width * toggley , -fudge]) {
        cylinder(d = togglediam, h = height + fudge2, center = false, $fn = 360);
        translate([-(togglewidth / 2), -(togglelength / 2), outerdepth + fudge]) {
            cube([togglewidth, togglelength, toggleheight + fudge]);
        }
    }
}