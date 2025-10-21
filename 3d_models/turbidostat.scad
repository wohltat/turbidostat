// ################# BASIC SETTINGS ##################
	// $fn = 256;
	$fn = 128;
	// $fn = 64;
	ext = 0.05; // walls can be thicker by this value
	eps = 0.02;


	filledLayersThickness = 1.2;
	layerHeight = 0.1;
	//explosion = 200*$t;
	explosion = 120*$t;
	// explosion = 120.0;
	

// ################# MODULES #########################
	module rounded_box(w, l, h, r, center=false) {
		inner_length = l - 2 * r;
		inner_width  = w - 2 * r;

		x_offset = (inner_width/2  + r)*((center)?0:1);
		y_offset = (inner_length/2 + r)*((center)?0:1);

		translate([x_offset, y_offset, 0])	
		hull() {
			translate([-inner_width / 2, -inner_length/2, 0]) cylinder(r=r, h=h);
			translate([+inner_width / 2, -inner_length/2, 0]) cylinder(r=r, h=h);
			translate([+inner_width / 2, +inner_length/2, 0]) cylinder(r=r, h=h);
			translate([-inner_width / 2, +inner_length/2, 0]) cylinder(r=r, h=h);
		}
	}

	module tube(h, r1, r2, center=false) {
		difference() {
		  cylinder(h=h, r=r1, center=center);

		  cylinder(h=h+2*eps, r=r2, center=center);
		}
	}

	module prism(l, w, h) {
		translate([0, l, 0]) rotate( a= [90, 0, 0]) 
		linear_extrude(height = l) polygon(points = [
			[0, 0],
			[w, 0],
			[0, h]
		], paths=[[0,1,2,0]]);
	}

	module elliptic_cylinder(h, a1, b1, a2, b2, center=false) {
		z_offset = ((center==true)?1:0)*(-h/2);
		translate([0, 0, z_offset])
		hull() {
			scale([1, b1/a1, 1])
			cylinder(h=eps, r=a1);

			translate([0, 0, h])
			scale([1, b2/a2, 1])
			cylinder(h=eps, r=a2);
		}
	}	

// ################# ACTIVE PARTS ####################
	bCap = 0;
	bOpticsHolder = 0;
	bTubeHolder = 1;
	bBoard = 0;
	bLaser = 0;
	bFanCap = 0;
	bFan = 0;
	bFanCover = 0;
	bGroundCover = 0;

	bViewingCutout = 0;
	bSupportStructure = 0;


// ====================== BOARD ===========================
	hBoard = 3;
	dBoard = 1.5;
	if(bBoard){
		color("green")
		translate([0, 0, 0.0*explosion])
		translate([0,0,hBoard])
		import("pcb.wrl");
	}

// ===================== FAN CAP ==========================
	wFan = 80;
	hFanCap = 10;
	dFanCap = 2;
	hInner = 10;
	rOuterHole = 4/2;
	screwBorder=1;

	if(bFanCap){
		color("gray")
		translate([0, 0, -0.1*explosion])
		translate([0,0,-hFanCap])
		difference() {
			union() {
				difference() {
					rounded_box(wFan, wFan, hFanCap, 2*rOuterHole);
					
					// cavity 			
					translate([rOuterHole, rOuterHole, -dFanCap])
					rounded_box(wFan-2*rOuterHole, wFan-2*rOuterHole, hFanCap, 2*rOuterHole);

					// cutout for fan cable
					translate([wFan-rOuterHole, 12, -eps])
					rounded_box(2*rOuterHole, 4*rOuterHole, hFanCap+2*eps, r=2*rOuterHole);

					//cutout for MOSFETs 
					translate([13, 55, 0])
					rounded_box(15, 22, hFanCap+eps, r=2*rOuterHole);

					//cutout for hall sensor 
					translate([55, (wFan-5)/2, 0])
					rounded_box(5, 5, hFanCap+eps, r=2);

					// screw holes	
					for( x=(rTubeHolder-2.5)*[-1, +1] ){
						for( y=(rTubeHolder-2.5)*[-1, +1]){
							translate([wFan/2+x, wFan/2+y, hFanCap-dFanCap/2])
							cylinder(h=dFanCap+2*eps, r1=2.2, r2=1, center=true);
						}
					}		
				}

				// tube for outer screw holes
				for( x=[0, wFan]+2*rOuterHole*[1,-1] ){
					for( y=[0, wFan]+2*rOuterHole*[1,-1] ){
						translate([x, y, 0])
						cylinder(h=hFanCap, r=2*rOuterHole, center=false);
					}
				}		
			}
			
			// outer screw holes
			for( x=[0, wFan]+2*rOuterHole*[1,-1] ){
				for( y=[0, wFan]+2*rOuterHole*[1,-1] ){
					translate([x, y, -eps])
					cylinder(h=100, r=rOuterHole, center=false);
				}
			}		
		}
	}

// =================== TUBE HOLDER ========================
	hTubeHolder = 90;
	hTubeHolderWindow = hTubeHolder-20-35;
	rTube = 25.8/2;
	dTubeHolderWall = 1.6;
	rTubeHolder = rTube + dTubeHolderWall;
	excentricity = 1.5;
	RimWidth = 8;
	rTubeHolderRim = rTubeHolder+RimWidth;
	rTubeHolderWindow = rTubeHolder/2;
	zOpticsHolder = 11;
	hOpticsHolder = 13;
	hMount = 7;
	rBeamPath = 3;
	dWindowPane = 1.2;
	wWindowPane = 8;
	hWindowPane = 16;



	if (bTubeHolder) {
		color("SlateGray")
		translate([0, 0, 0.1*explosion])
		difference() {
			union() {
				
				// main cylinder
				translate([wFan/2, wFan/2, 0])
				// cylinder(h=hTubeHolder, r=rTubeHolder+ext, center=true);
				// slightliy elliptical to hold the tube
				elliptic_cylinder(h=hTubeHolder, a1=rTubeHolder, b1=rTubeHolder,
				                                a2=rTubeHolder + excentricity/2, b2=rTubeHolder - excentricity/2,
				                                center=false);
			
				// rim
				translate([wFan/2, wFan/2, -hMount/2 + zOpticsHolder])
				cylinder(h=hMount, r1=rTubeHolder, r2=rTubeHolderRim, center=true);

				// base
				translate([wFan/2, wFan/2, zOpticsHolder/2-eps])
				cube([2*rTubeHolder, 2*rTubeHolder, zOpticsHolder], center=true);

				// pocket for window pane
				translate([wFan/2, wFan/2, zOpticsHolder+hOpticsHolder/2-eps])
				rotate([0, 0, 45]) 
				// slope roof 
				hull(){
					cube([hOpticsHolder, 2*(rTubeHolder+dWindowPane), hOpticsHolder], center=true);
					translate([0, 0, 20])
					cube([hOpticsHolder, (rTubeHolder+dWindowPane), 1], center=true);
				}
			}

			removeFrame = 1;
			// pocket for window pane cutout - laser/sensor B side
			translate([wFan/2, wFan/2, zOpticsHolder+hWindowPane/2-eps])
			rotate([0, 0, 45]) 
			translate([0, rTubeHolder+dWindowPane/2-0.3+removeFrame/2, 0])
			cube([wWindowPane+0.4, dWindowPane+removeFrame, hWindowPane], center=true);

			// pocket for window pane cutout - Sensor A side
			translate([wFan/2, wFan/2, zOpticsHolder+hWindowPane/2-eps])
			rotate([0, 0, -(90+45)]) 
			translate([0, rTubeHolder+dWindowPane/2-0.3+removeFrame/2, 0])
			cube([wWindowPane+0.4, dWindowPane+removeFrame, hWindowPane], center=true);

			// // push-out-hole for window B
			// translate([wFan/2, wFan/2, 0])
			// rotate([0, 0, 45]) 
			// translate([0, rTubeHolder+6*ext, 0.2 -2*eps])
			// cylinder(h=zOpticsHolder+hOpticsHolder/2, r=dWindowPane/2, center=false, $fn=20);

			// // push-out-hole for window A
			// translate([wFan/2, wFan/2, 0])
			// rotate([0, 0, -(90+45)]) 
			// translate([0, rTubeHolder+6*ext, 0.2 -2*eps])
			// cylinder(h=zOpticsHolder+hOpticsHolder/2, r=dWindowPane/2, center=false, $fn=20);

			// cutout for arduino
			// translate([wFan/2, wFan/2, hTubeHolder/2+2])
			cube([wFan, +wFan/2 - rTubeHolder-0.8, hTubeHolder/2]);

			if(bViewingCutout){
				// translate([wFan/2, wFan/2, hTubeHolder/2+2])
				cube([wFan, +wFan/2, hTubeHolder/2]);
			}

			// cutout for sensor B
			translate([wFan/2-24, wFan/2, 0])
			rotate([0, 0, 45]) 
			cube([10, 10, hTubeHolder/2]);

			// space for tube
			// cylinder(h=hTubeHolder, r=rTube+4*ext, center=true);
			translate([wFan/2, wFan/2, 2 + hCone-eps])
			elliptic_cylinder(h=hTubeHolder - hCone, 
				a1=rTube, b1=rTube,
				a2=rTube + excentricity/2, b2=rTube - excentricity/2);

			// space silicone plate
			translate([wFan/2, wFan/2, 2+0.5-eps])
			cylinder(h=1, r=26/2, center=true);

			// space for tube - conical part
			hCone = 2;
			rConeUpper = rTube;
			rConeLower = rTube  - 0.3;
			translate([wFan/2, wFan/2, 2])
			cylinder(h=hCone, r1=rConeLower , r2=rConeUpper, center=false);
			
			// Windows
			translate([wFan/2-1.5*rTube, wFan/2, hTubeHolder-10 -hTubeHolderWindow/2])
			hull(){	
				translate([0, 0, hTubeHolderWindow/2])
				rotate([0, 90, 0])
				cylinder(h=3*rTube, r=rTubeHolderWindow/4, center=false);

				rotate([90, 0, 90])
				rounded_box(15, hTubeHolderWindow, 3*rTube, rTubeHolderWindow, center=true);
			}

			// cutout for beampath
			translate([wFan/2, wFan/2, zOpticsHolder+hOpticsHolder/2])
			rotate([90, 0, 45])
			cylinder(h=hTubeHolder, r=rBeamPath, center=true);

			// holes for screws (ears)
			translate([wFan/2, wFan/2, zOpticsHolder+hOpticsHolder/2])
			union() {
				translate([0, rOpticsHolder+2.8, -hOpticsHolder/2+dEars/2])
				cylinder(h=8*dEars, r=1, center=true);
				translate([rOpticsHolder+2.8, 0, -hOpticsHolder/2+dEars/2])
				cylinder(h=8*dEars, r=1, center=true);
				rotate([0, 0, 30]) 
				translate([-rOpticsHolder-2.8, 0, -hOpticsHolder/2+dEars/2])
				cylinder(h=8*dEars, r=1, center=true);
			}

			// holes for screws (plate)
			translate([wFan/2, wFan/2, 0])
			union() {
				for( x=(rTubeHolder-2.5)*[-1, +1] ){
					for( y=(rTubeHolder-2.5)*[-1, +1]){
						translate([x, y, 0])
						cylinder(h=8*dEars, r=1, center=true);
					}
				}
			}
		}
	}

// ====================== LASER ===========================
	lLaser = 20;
	if(bLaser){
		color("gold")
		translate([0, 0, 0.25*explosion])
		translate([wFan/2, wFan/2, zOpticsHolder+hOpticsHolder/2])
		rotate([90, 0, 180+45])
		translate([0, 0, rTubeHolder + lLaser/2 + 10.5])
		cylinder(h=lLaser, r=rLaser, center=true);
	}

// =================== OPTICS HOLDER ======================
	rBeamPath2 = 3.4/2;
	lArm1 = 25;
	lArm2 = 20;
	rLaser = 10/2-0.1;
	ringThickness = 2;
	rOpticsHolder = rTubeHolder+ringThickness;
	rHalfMirror = rTubeHolder+ringThickness+10/2 - 0.5;
	dEars = 1.5;
	hSensor = 4.5;
	wSensor = 5.5;
	dSensor = 2.6;
	if (bOpticsHolder) {
		color("Silver")
		translate([0, 0, 0.25*explosion])
		difference() {
			translate([wFan/2, wFan/2, zOpticsHolder+hOpticsHolder/2])
			union() {
				cylinder(h=hOpticsHolder, r=rTubeHolder+ringThickness, center=true);

				// laser and sensor B holder
				rotate([0, 0, 45])
				translate([0, rTubeHolder+lArm1/2, 0])
				cube([hOpticsHolder, lArm1, hOpticsHolder], center=true);

				rotate([0, 0, 45])
				translate([-10, rHalfMirror+1, 0])
				cube([7, 10, hOpticsHolder], center=true);

				// // Laser adjustment screw
				// rotate([0, 0, 45])
				// translate([-(hOpticsHolder+3)/2, rTubeHolder+ringThickness+10/2+15, 0])
				// rotate([0, 90, 0]) 
				// cylinder(r=2, h=3, center=true);
				
				// sensor A holder
				rotate([0, 0, 180+45])
				translate([0, rTubeHolder+lArm2/2, 0])
				cube([10, lArm2, hOpticsHolder], center=true);

				// ears for screws
				translate([0, rOpticsHolder, -hOpticsHolder/2+dEars/2])
				cylinder(h=dEars, r=RimWidth-ringThickness, center=true);
				translate([rOpticsHolder, 0, -hOpticsHolder/2+dEars/2])
				cylinder(h=dEars, r=RimWidth-ringThickness, center=true);
				rotate([0, 0, 30]) 
				translate([-rOpticsHolder, 0, -hOpticsHolder/2+dEars/2])
				cylinder(h=dEars, r=RimWidth-ringThickness, center=true);

				// pocket for window pane
				rotate([0, 0, 45])
				cube([hOpticsHolder+3, 2*(rTubeHolder+dWindowPane)+4, hOpticsHolder], center=true);

			}

			translate([wFan/2, wFan/2, zOpticsHolder+hOpticsHolder/2])
			rotate([0, 0, 45]){
				if(bViewingCutout){
					// viewing cutout
					translate([0, rTubeHolder+lArm1/2, 7])
					cube([hOpticsHolder+6+eps, lArm1+eps, hOpticsHolder], center=true);
		
					// viewing cutout 2
					rotate([0, 0, 180])
					translate([0, rTubeHolder+lArm2/2, 7])
					cube([10+1, lArm2-8, hOpticsHolder], center=true);
				}

				// pocket for window pane cutout
				cube([hOpticsHolder+4*ext, 2*(rTubeHolder+dWindowPane)+4*ext, hOpticsHolder+eps], center=true);

				// hole for half mirror block
				translate([0, rHalfMirror-0.5, 2])
				rotate([0, 0, +45]) 
				cube([wWindowPane+0.4, dWindowPane+4*ext, hOpticsHolder], center=true);

				// hole for sensor B
				// translate([-10, rHalfMirror+1, (hOpticsHolder-hSensor)/4+eps])
				// cube([dSensor, wSensor, (hSensor+hOpticsHolder)/2], center=true);

				translate([-10+ext, rHalfMirror+1, (-hSensor)/2-eps])
				cube([dSensor+2*ext, wSensor+2*ext, (hSensor+hOpticsHolder)/2], center=true);

				// hole for sensor A ##################
				// rotate([0, 0, 180])
				// translate([0, rTubeHolder+lArm2*0.8, (hOpticsHolder-hSensor)/4+eps])
				// cube([wSensor, dSensor, (hSensor+hOpticsHolder)/2], center=true);

				rotate([0, 0, 180])
				translate([0, rTubeHolder+lArm2*0.8-ext, (-hSensor)/2-eps])
				cube([wSensor+2*ext, dSensor+2*ext, (hSensor+hOpticsHolder)/2], center=true);
				
				// free space in the middle
				cylinder(h=hOpticsHolder+1, r=rTubeHolder + 3*ext, center=true);
				
				// cutout for beampath
				rotate([90, 0, 0])
				cylinder(h=60, r=rBeamPath2, center=true);

				// cutout for beampath to sensor B
				translate([-5, rHalfMirror+1, 0])
				rotate([90, 0, 90])
				cylinder(h=10, r=rBeamPath2, center=true);

				// cutout for laser
				rotate([90, 0, 180])
				translate([0, 0, rTubeHolder + 41/2 + 14])
				cylinder(h=49, r=rLaser, center=true);

				// // cutout for Laser adjustment screw
				// // rotate([0, 0, 45])
				// translate([-(hOpticsHolder+3)/2, rTubeHolder+ringThickness+10/2+15, 0])
				// rotate([0, 90, 0]) 
				// cylinder(r=0.8, h=8, center=true);

			}

			// Ring opening
			translate([wFan/2, wFan/2-rTubeHolder, zOpticsHolder+hOpticsHolder/2-4])
			cube([18, wFan/2, +hOpticsHolder], center=true);
			
			// ear holes for screws
			translate([wFan/2, wFan/2, zOpticsHolder+hOpticsHolder/2])
			union() {
				translate([0, rOpticsHolder+2.8, -hOpticsHolder/2+dEars/2])
				cylinder(h=2*dEars, r=1, center=true);
				translate([rOpticsHolder+2.8, 0, -hOpticsHolder/2+dEars/2])
				cylinder(h=2*dEars, r=1, center=true);
				rotate([0, 0, 30]) 
				translate([-rOpticsHolder-2.8, 0, -hOpticsHolder/2+dEars/2])
				cylinder(h=2*dEars, r=1, center=true);
			}
			
		}	
	}

// ======================= CAP ============================
	rCapOutside = 180;
	oOutside = -rCapOutside+90;
	dCap = 2;
	hCap = 40;
	oInsideWallxy = 300;
	oInsideWallz = 50;
	rCapInside = sqrt(pow(oInsideWallz,2) + pow(oInsideWallxy+wFan/2,2))+6;
	oInsideTopxy = 60;
	oInsideTopz = 180;
	rCapInsideTop = sqrt(pow(oInsideTopz+hCap,2) + pow(oInsideTopxy,2));
	xConnectors = -14;
	hNut = 2.3;
	rScrewHole = 1.06;
	rM3Nut = 6/2 + 0.4;
	x_usb = 1.8;
	y_usb = 10.1;
	z_usb = hBoard + 14.2;
	w_usb = 11.7;
	h_usb = 8.5;
	w_usb_inner = 8.0;
	h_usb_inner = 4.1;
	d_usb = 1;
	hScrewSocket = 20;

	if(bCap){
		color("gray", a=1)
		translate([0, 0, 1.0*explosion])
		difference() {
			union() {
				difference() {
					// shell
					intersection() {
						translate([wFan/2,+oOutside,0])
						sphere(r=rCapOutside, center=true);
					
						translate([+oOutside,wFan/2,0])
						sphere(r=rCapOutside, center=true);
					
						translate([wFan-oOutside,wFan/2,0])
						sphere(r=rCapOutside, center=true);
					
						translate([wFan/2,wFan-oOutside,0])
						sphere(r=rCapOutside, center=true);
					
						translate([wFan/2,wFan/2, -rCapOutside+hCap])
						sphere(r=rCapOutside, center=true);
					}
					
					// remove lower half
					translate([-wFan/2, -wFan/2, -rCapOutside])
					cube([2*wFan, 2*wFan, rCapOutside]);
			
					// viewing window
					if(bViewingCutout){
						translate([-wFan/2, -wFan/2, 20-15])
						cube([2*wFan, 2*wFan, rCapOutside]);
					}
			
					// main space
					intersection() {		
						translate([wFan/2-oInsideWallxy, wFan/2, -oInsideWallz])
						sphere(r=rCapInside, center=true);
						translate([wFan/2+oInsideWallxy, wFan/2, -oInsideWallz])
						sphere(r=rCapInside, center=true);
						translate([wFan/2, wFan/2-oInsideWallxy, -oInsideWallz])
						sphere(r=rCapInside, center=true);
						translate([wFan/2, wFan/2+oInsideWallxy, -oInsideWallz])
						sphere(r=rCapInside, center=true);
						
						// support with maximal slope
						// translate([wFan/2,wFan/2, -rCapInsideTop+hCap])
						// sphere(r=rCapInsideTop-dFanCap, center=true);
						translate([wFan/2-oInsideTopxy, wFan/2, -oInsideTopz])
						sphere(r=rCapInsideTop, center=true);
						translate([wFan/2+oInsideTopxy, wFan/2, -oInsideTopz])
						sphere(r=rCapInsideTop, center=true);
						translate([wFan/2, wFan/2-oInsideTopxy, -oInsideTopz])
						sphere(r=rCapInsideTop, center=true);
						translate([wFan/2, wFan/2+oInsideTopxy, -oInsideTopz])
						sphere(r=rCapInsideTop, center=true);
					}
			
					// cutout for tube holder
					translate([wFan/2, wFan/2, hTubeHolder/2])
					cylinder(h=hTubeHolder, r=rTubeHolder+2*ext+0.2, center=true, $fn=$fn/4);
				}//difference

				intersection() {
					// connections
					translate([xConnectors, 3, 0])
					cube([13.8, 65, 25]);
					
					translate([wFan-oOutside,wFan/2,0])
					sphere(r=rCapOutside, center=true);
				}
				// usb cable cavity
				translate([-5+x_usb+d_usb, y_usb-2*d_usb - (w_usb-w_usb_inner)/2, z_usb-2*d_usb - (h_usb-h_usb_inner)/2])
				// translate([-18+x_usb, y_usb - (w_usb-w_usb_inner)/2, z_usb - (h_usb-h_usb_inner)/2])
				cube     ([ 5,             w_usb+4*d_usb, h_usb+4*d_usb]);

				// screw socket (beds for nuts)
				for( x=[0, wFan]+2*rOuterHole*[1,-1] ){
					for( y=[0, wFan]+2*rOuterHole*[1,-1] ){
						translate([x, y, hScrewSocket/2 + hBoard + dBoard])
						cylinder(r=2*rOuterHole, h=hScrewSocket, center=true, $fn=16);
						translate([x, y, hScrewSocket/2 + hBoard+dBoard])
						rotate([0, 0, 180 + atan2(sign(y-wFan/2), sign(x-wFan/2))])
						translate([-0*rOuterHole, 0, 0])
						#linear_extrude(height=hScrewSocket/2, center=true, convexity=10, twist=0) {
							polygon( points=[[0, 2*rOuterHole], [0, -2*rOuterHole], [-1*rOuterHole, -5*rOuterHole], [-4*rOuterHole, 0], [-1*rOuterHole, 5*rOuterHole] ]);
						}
						//#cube([2*rOuterHole, 4*rOuterHole, hScrewSocket], center=true);
					}
				}	

				// corner fill
				translate([wFan/2, wFan/2, 0])
				for(alpha=[0,1,2,3]*90){
					rotate([0, 0, 45+alpha])
					translate([-wFan/2-22, 0, 0])
					scale([0.8, 1, 1]) 
					rotate([90, 0, 45])
					prism( hBoard+dBoard+hNut+hNut, 10 , 10);
				}
				
				if(bSupportStructure){
					// support for nut beds
					difference() {
						union() {
							// distance ring
							translate([2*rOuterHole, 2*rOuterHole, 0])
							cylinder(r=2*rOuterHole, h=hBoard+dBoard-2*layerHeight, center=false, $fn=16);
							translate([wFan-2*rOuterHole, 2*rOuterHole, 0])
							cylinder(r=2*rOuterHole, h=hBoard+dBoard-2*layerHeight, center=false, $fn=16);
							translate([wFan-2*rOuterHole, wFan-2*rOuterHole, 0])
							cylinder(r=2*rOuterHole, h=hBoard+dBoard-2*layerHeight, center=false, $fn=16);
							translate([2*rOuterHole, wFan-2*rOuterHole, 0])
							cylinder(r=2*rOuterHole, h=hBoard+dBoard-2*layerHeight, center=false, $fn=16);
						}
						
						// screw hole in distance ring
						for( x=[0, wFan]+2*rOuterHole*[1,-1] ){
							for( y=[0, wFan]+2*rOuterHole*[1,-1] ){
								translate([x, y,-eps])
								cylinder(h=hBoard+1, r=rOuterHole, center=false, $fn=20);
							}
						}		
					}
					
					

					// // anti corner warping structure
					// translate([wFan/2, wFan/2, 0])
					// for(alpha=[0,1,2,3]*90){
					// 	rotate([0, 0, 45+alpha])
					// 	translate([-wFan/2-43, -3, 0])
					// 	cube(size=[20, 6 , 5], center=false);
					// }

				}

			}//union

			// // connections
			// translate([-17, 3+dCap, dCap])
			// cube([17, 65-2*dCap, 21]);

			// translate([0, 0, -eps])
			// #cube([17, 70, 2]);

			// jack cutout
			// translate([xConnectors-1, 28, 2])
			// cube([18, 10, 11]);
			translate([xConnectors-1, 33, hBoard + 8.5])
			rotate([0, 90, 0])
			cylinder(h=14, r=12/2, center=false, $fn=32);
			translate([xConnectors-1, 33, hBoard + 8.5])
			rotate([0, 90, 0])
			cylinder(h=20, r=8/2, center=false, $fn=32);

			// USB cutout
			translate([-15.6, y_usb,       z_usb])
			cube     ([ 18, w_usb_inner, h_usb_inner]);
			translate([-18+x_usb, y_usb - (w_usb-w_usb_inner)/2, z_usb - (h_usb-h_usb_inner)/2])
			cube     ([ 18,       w_usb, h_usb]);


			// pumps connector
			// old connector
			// r_pump_connector_inner = 16.0/2;
			// r_pump_connector_outer = 21.0/2;
			// new s-video connector
			r_pump_connector_inner = 11.0/2;
			r_pump_connector_outer = 14.0/2;
			translate([xConnectors-8, 52, hBoard + 12])
			rotate([0, 90, 0])
			cylinder(h=20, r=r_pump_connector_inner, center=false, $fn=32);

			translate([xConnectors-12.8, 52, hBoard + 12])
			rotate([0, 90, 0])
			cylinder(h=20, r=r_pump_connector_outer, center=false, $fn=32);

			translate([xConnectors+8.2, 52, hBoard + 12])
			rotate([0, 90, 0])
			cylinder(h=20, r=24/2, center=false, $fn=32);

			translate([xConnectors+8.2, 40.2, hBoard + 12 - 30])
			cube(size=[10, 24, 30], center=false);

			translate([-1, wFan/2, (hBoard+dBoard)/2-eps])
			cube(size=[2, wFan, hBoard+dBoard], center=true);


			// // M3 Nuts
			// translate([2*rOuterHole, 2*rOuterHole, hBoard+dBoard+1.5*hNut+eps])
			// #cylinder(r=rM3Nut, h=hNut, $fn=6, center=true);

			// translate([wFan-2*rOuterHole, 2*rOuterHole, hBoard+dBoard+1.5*hNut+eps])
			// #cylinder(r=rM3Nut, h=hNut, $fn=6, center=true);

			// translate([wFan-2*rOuterHole, wFan-2*rOuterHole, hBoard+dBoard+1.5*hNut+eps])
			// #cylinder(r=rM3Nut, h=hNut, $fn=6, center=true);

			// translate([2*rOuterHole, wFan-2*rOuterHole, hBoard+dBoard+1.5*hNut+eps])
			// #cylinder(r=rM3Nut, h=hNut, $fn=6, center=true);

			// screw holes ...		
			for( x=[0, wFan]+2*rOuterHole*[1,-1] ){
				for( y=[0, wFan]+2*rOuterHole*[1,-1] ){
					// ...for screw ...
					translate([x, y, hBoard+1.4+1-eps])
					cylinder(h=10, r=rScrewHole, center=false, $fn=20);
					// ... guidance funnel
					translate([x, y, hBoard+1.4])
					cylinder(h=1, r2=rScrewHole, r1=1.8*rOuterHole, center=false, $fn=20);
				}
			}		

		}//difference
	}

// ======================= FAN ============================
	// hFan = 24.5;
	hFan = 15;
	if(bFan){
		color("LightSteelBlue")
		translate([0, 0, -0.2*explosion])
		difference() {
			translate([0, 0, -hFanCap-hFan])
			rounded_box(wFan, wFan, hFan, 2*rOuterHole);
			
			// screw holes				
			translate([2*rOuterHole, 2*rOuterHole, -1.05*hFanCover])
			cylinder(h=1.1*hFanCover, r=rOuterHole, center=false);
			translate([wFan-2*rOuterHole, 2*rOuterHole, -1.05*hFanCover])
			cylinder(h=1.1*hFanCover, r=rOuterHole, center=false);
			translate([2*rOuterHole, wFan-2*rOuterHole, -1.05*hFanCover])
			cylinder(h=1.1*hFanCover, r=rOuterHole, center=false);
			translate([wFan-2*rOuterHole, wFan-2*rOuterHole, -1.05*hFanCover])
			cylinder(h=1.1*hFanCover, r=rOuterHole, center=false);

			// central hole
			translate([wFan/2, wFan/2, -hFanCover/2])
			cylinder(h=1.1*hFanCover, r=wFan/2-2, center=true);
		}
	}

// ==================== FAN COVER =========================
	dFanCover = 2;
	hFanCover = hFan+hFanCap+3;
	lFanCover = wFan+4;
	if(bFanCover){
		color("gray")
		translate([0, 0, -0.6*explosion])
		difference() {
			intersection() {
				translate([wFan/2,+oOutside, -hFanCover/2])
				cylinder(r=rCapOutside, h= hFanCover, center=true);
			
				translate([+oOutside,wFan/2, -hFanCover/2])
				cylinder(r=rCapOutside, h= hFanCover, center=true);
			
				translate([wFan-oOutside,wFan/2, -hFanCover/2])
				cylinder(r=rCapOutside, h= hFanCover, center=true);
			
				translate([wFan/2,wFan-oOutside, -hFanCover/2])
				cylinder(r=rCapOutside, h= hFanCover, center=true);
			}
			
			intersection() {
				translate([wFan/2,+oOutside, -hFanCover/2])
				cylinder(r=rCapOutside-dFanCover, h= hFanCover+dFanCover, center=true);
			
				translate([+oOutside,wFan/2, -hFanCover/2])
				cylinder(r=rCapOutside-dFanCover, h= hFanCover+dFanCover, center=true);
			
				translate([wFan-oOutside,wFan/2, -hFanCover/2])
				cylinder(r=rCapOutside-dFanCover, h= hFanCover+dFanCover, center=true);
			
				translate([wFan/2,wFan-oOutside, -hFanCover/2])
				cylinder(r=rCapOutside-dFanCover, h= hFanCover+dFanCover, center=true);

				union() {
					translate([wFan/2, wFan/2,-hFanCover/2+dFanCover])
					cube(size=[wFan*1.5, wFan-20, hFanCover], center=true);
		
					translate([wFan/2, wFan/2,-hFanCover/2+dFanCover])
					cube(size=[wFan-20, wFan*1.5, hFanCover], center=true);
				}
				
			}
			
			translate([-ext, -ext, -hFanCover-1])
			rounded_box(wFan+8*ext, wFan+8*ext, hFanCover+2, 2*rOuterHole);

			translate([-ext-4/2, -ext-4/2, -hFanCover-eps])
			rounded_box(lFanCover+2*ext, lFanCover+2*ext, dFanCover+2*eps, 2*rOuterHole);
		}

		if(bSupportStructure){
			// support for nut beds
			difference() {
				union() {
					// distance ring
					translate([2*rOuterHole, 2*rOuterHole, -hFanCover])
					cylinder(r=2*rOuterHole-0.4, h=hFanCover, center=false, $fn=16);
					translate([wFan-2*rOuterHole, 2*rOuterHole, -hFanCover])
					cylinder(r=2*rOuterHole-0.4, h=hFanCover, center=false, $fn=16);
					translate([wFan-2*rOuterHole, wFan-2*rOuterHole, -hFanCover])
					cylinder(r=2*rOuterHole-0.4, h=hFanCover, center=false, $fn=16);
					translate([2*rOuterHole, wFan-2*rOuterHole, -hFanCover])
					cylinder(r=2*rOuterHole-0.4, h=hFanCover, center=false, $fn=16);
				}
				
				// screw hole in distance ring
				for( x=[0, wFan]+2*rOuterHole*[1,-1] ){
					for( y=[0, wFan]+2*rOuterHole*[1,-1] ){
						translate([x, y,-eps-hFanCover])
						cylinder(h=hFanCover+1, r=2*rOuterHole-1.6, center=false, $fn=20);
					}
				}		
			}
		}
	}

// =================== GROUND COVER =======================
	if(bGroundCover){
		color("darkgray")
		translate([0, 0, -0.8*explosion])
		// uncomment for DXF export
		// projection(cut = true)
		// translate([0, 0, hFanCover])
		difference() {
			// base plate
			translate([(wFan-lFanCover)/2, (wFan-lFanCover)/2, -hFanCover])
			#rounded_box(lFanCover, lFanCover, 0.9*dFanCover, 2*rOuterHole);
			
			// screw holes		
			for( x=[0, wFan]+2*rOuterHole*[1,-1] ){
				for( y=[0, wFan]+2*rOuterHole*[1,-1] ){
					translate([x, y, -hFanCover-eps])
					cylinder(h=dFanCover, r1=9/2, r2=5.5/2, center=false);
				}
			}
		}
	}
