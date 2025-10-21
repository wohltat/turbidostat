// Parameters
	ext=0.1;
	eps=0.02;

	bLid = 0;
	bCup = 1;
	bStand = 0;


	hPlug = 25;
	wStand = 40;

// Modules
	module bore_holes(){
		for(i=[1:4]){
				rotate([0, 0, 90*i]) 
				translate([wStand*0.35, wStand*0.35, 0])
				#cylinder(r=1, h=10, center=true);
			}	
	}
	module needle_holes(){
		for(x=dPorts*[-1, 1], y=dPorts*[-1,1])
			translate([x,y,0])
			cylinder(r=2/2+ext, h=50, center=true, $fn=12);
	}

// LID
	if(bLid){
		translate([0, 0, hPlug + 2/2])
		difference() {
			cube(size=[wStand, wStand, 2], center=true);
			needle_holes();
		}
		
	}

// CUP
	if(bCup){
		difference() {
			union() {
				// outer shell
				cylinder(r=28/2, h=hPlug, $fn=32);
				translate([0, 0, 1])
				//base
				cube(size=[wStand, wStand, 2], center=true);
			}
			
			// inner cone
			translate([0, 0, -eps])
			#cylinder(r1=20/2, r2=26/2, h=25+2*eps, $fn=128);

			bore_holes();	
		}
	}	

// STAND
	dPorts = 4.5;
	hStand = 30;
	if(bStand){

		translate([0, 0, -hStand/2])
		difference() {
			cube(size=[wStand, wStand, hStand], center=true);

			needle_holes();
			bore_holes();	
		}
	}

