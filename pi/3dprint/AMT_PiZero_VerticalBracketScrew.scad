/* 
 * Bracket to fix object on vertical 25 * 3 mm aluminium bar
 *
 * This design produces a bracket that fits over a 25 x 3 mm aluminium bar.
 * See https://amt.hobern.net/ for more detail.
 *
 * Author: Donald Hobern
 * Copyright: Copyright 2021, Donald Hobern
 * License: CC0
 * Version: 1.0.0
 * Email: dhobern@gmail.com
 */

// From AMT_PiZero_BaseBracket 
length = 60; 
width = 25;

// Slightly looser than for the tightly clamped fittings
barwidth = 25.4;
bardepth = 3.4;
thickness = 6;
outerthickness = 8;
screwdiam = 2.8;
bevel = 2;
slotx = (length - barwidth) / 2;

centrelength = barwidth + 2 * thickness;

// To adjust design and ensure that the design is at least mostly manifold.
fudge = 0.1;
fudge2 = 0.2;

$fn = 360;

rotate([90, 0, 0]) {
    difference() {
        // main block
        union() {
            cube([length, width, outerthickness]);
            translate([(length - centrelength) / 2, 0, 0]) {
                cube([centrelength, width, outerthickness + bardepth + thickness]);
            }
        }
        translate([slotx, -fudge, outerthickness]) {
            cube([barwidth, width + fudge2, bardepth]);
        }
        for (i = [(length - centrelength) / 4, length - (length - centrelength) / 4]) {
            for(j = [width * 0.25, width * 0.75]) {
                translate([i, j, -fudge]) {
                    cylinder(d = screwdiam, h = outerthickness + fudge2);
                }
            }
        }
        polyhedron(points = [[slotx - bevel, -fudge, outerthickness - bevel], 
                             [length - slotx + bevel, -fudge, outerthickness - bevel],
                             [length - slotx + bevel, -fudge, outerthickness + bardepth + bevel],
                             [slotx - bevel, -fudge, outerthickness + bardepth + bevel],
                             [slotx, bevel - fudge, outerthickness], 
                             [length - slotx, bevel - fudge, outerthickness],
                             [length - slotx, bevel - fudge, outerthickness + bardepth],
                             [slotx, bevel - fudge, outerthickness + bardepth]],
                   faces = [[0,1,2,3],[4,5,1,0],[7,6,5,4],[5,6,2,1],[6,7,3,2],[7,4,0,3]],  
                   convexity = 15);
        translate([length, width, 0]) rotate([ 0, 0, 180]) {
            polyhedron(points = [[slotx - bevel, -fudge, outerthickness - bevel], 
                                 [length - slotx + bevel, -fudge, outerthickness - bevel],
                                 [length - slotx + bevel, -fudge, outerthickness + bardepth + bevel],
                                 [slotx - bevel, -fudge, outerthickness + bardepth + bevel],
                                 [slotx, bevel - fudge, outerthickness], 
                                 [length - slotx, bevel - fudge, outerthickness],
                                 [length - slotx, bevel - fudge, outerthickness + bardepth],
                                 [slotx, bevel - fudge, outerthickness + bardepth]],
                       faces = [[0,1,2,3],[4,5,1,0],[7,6,5,4],[5,6,2,1],[6,7,3,2],[7,4,0,3]],  
                       convexity = 15);
        }
    }
    
}