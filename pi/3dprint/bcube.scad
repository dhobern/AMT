module beveledcube(x=10, y=10, z=10, bx=2, by=2, bz=2) {
   f = 0.1;
    difference() {
        cube([x, y, z]);
        translate([0,0,-f]) linear_extrude(height=z+2*f) {
            polygon([[-f,-f],[bx+f,-f],[-f,by+f]]);
            polygon([[x-bx-f,-f],[x+f,-f],[x+f,by+f]]);
            polygon([[x-bx-f,y+f],[x+f,y+f],[x+f,y-by-f]]);
            polygon([[-f,y+f],[bx+f,y+f],[-f,y-by-f]]);
        }
        rotate([0,90,0]) translate([0,0,-f]) linear_extrude(height=x+2*f) {
            polygon([[f,-f],[-bz-f,-f],[-f,by+f]]);
            polygon([[-z-f,-f],[-z-f,by+f],[-z+bz+f,-f]]);
            polygon([[f,y+f],[-bz-f,y+f],[f,y-by-f]]);
            polygon([[-z-f,y+f],[-z-f,y-by-f],[-z+bz+f,y+f]]);
        }
        rotate([-90,0,0]) translate([0,0,-f]) linear_extrude(height=y+2*f) {
            polygon([[-f,f],[bx+f,f],[-f,-bz-f]]);
            polygon([[x-bx-f,f],[x+f,f],[x+f,-bz-f]]);
            polygon([[-f,-z-f],[bx+f,-z-f],[-f,-z+bz+f]]);
            polygon([[x-bx-f,-z-f],[x+f,-z-f],[x+f,-z+bz+f]]);
        }
    }

}
beveledcube(y=20,z=30,by=1,bz=6);