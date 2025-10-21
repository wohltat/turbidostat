"""Turbidostat FreeCAD model generator."""

# App.setActiveDocument('Turbidostat')
# import PartDesign
from FreeCAD import Base
from numpy import *
import numpy as np
# from exceptions import ReferenceError
import Mesh


def clear_all():
    """Clear document."""
    doc = App.ActiveDocument
    for obj in doc.Objects:
        try:
            doc.removeObject(obj.Name)
        except (RuntimeError, ReferenceError) as e:
            print('Exception: ' + str(e))
            pass
cla = clear_all

try:
    App.setActiveDocument('Turbidostat')
    cla()

except (Base.FreeCADError, RuntimeError):
    Gui.activateWorkbench('PartDesignWorkbench')
    App.newDocument('Turbidostat')

a = App.ActiveDocument = App.getDocument('Turbidostat')
g = Gui.ActiveDocument = Gui.getDocument('Turbidostat')


def mag(x):
    """Magnitude/Norm/length of an array."""
    x = array(x)
    return np.sqrt(x.dot(x))


def cut(obj_a, obj_b, name='Cut', a=a, g=g):
    """Difference obj_b from obj_a."""
    return boolean(obj_a, obj_b, 'Cut', name=name, a=a, g=g)


def fuse(obj_a, obj_b, name='Fuse', a=a, g=g):
    """Merge obj_a and obj_b."""
    return boolean(obj_a, obj_b, 'Fuse', name=name, a=a, g=g)


def common(obj_a, obj_b, name='Common', a=a, g=g):
    """Intersect obj_a and obj_b."""
    return boolean(obj_a, obj_b, 'Common', name=name, a=a, g=g)


def boolean(obj_a, obj_b, boolean_type, name='Boolean', a=a, g=g):
    """Boolean operation between obj_a and obj_b.

    Possible values for boolean_type are 'Cut', 'Fuse' or 'Common'.
    """
    boolean = obj_a.newObject('PartDesign::Boolean', name)
    # a.recompute()
    # g.setEdit('Boolean', 0)
    obj_a.Tip.ViewObject.show()
    Gui.Selection.clearSelection()
    boolean.ViewObject.ShapeColor   = obj_a.ViewObject.ShapeColor
    boolean.ViewObject.LineColor    = obj_a.ViewObject.LineColor
    boolean.ViewObject.PointColor   = obj_a.ViewObject.PointColor
    boolean.ViewObject.Transparency = obj_a.ViewObject.Transparency
    boolean.ViewObject.DisplayMode  = obj_a.ViewObject.DisplayMode
    if type(obj_b) == list:
        obj_b_list = obj_b
    else:
        obj_b_list = [obj_b, ]
    boolean.setObjects(obj_b_list)
    boolean.Type = boolean_type
    a.recompute()
    g.resetEdit()
    return boolean


def box(size=r_[10, 10, 10], pos=r_[0, 0, 0], axis=r_[0, 0, 1], angle=0, center=r_[0, 0, 0], name='Box', a=a, g=g):
    """Create box/cuboid."""
    box = a.addObject('PartDesign::AdditiveBox', name)
    box.Length = float(size[0])
    box.Width  = float(size[1])
    box.Height = float(size[2])
    box.Placement = App.Placement(App.Vector(pos), App.Rotation(App.Vector(axis), angle), App.Vector(center))
    return box


def cylinder(r=10, h=10, c_angle=360, pos=r_[0, 0, 0], axis=r_[0, 0, 1], angle=0, center=r_[0, 0, 0], name='Cylinder'):
    """Create cylinder.

    Args:
        r: Radius of the cylinder.
        h: Height of the cylinder.
        angle: Angle of the base of the cylinder in degree.

    Returns:
        This is a description of what is returned.radius r, position pos, name
    """
    cylinder = a.addObject('PartDesign::AdditiveCylinder', name)
    cylinder.Radius = r
    cylinder.Height = h
    cylinder.Angle = c_angle
    cylinder.Placement = App.Placement(App.Vector(pos), App.Rotation(App.Vector(axis), angle), App.Vector(center))
    return cylinder


def sphere(r=10, pos=r_[0, 0, 0], axis=r_[0, 0, 1], angle=0, center=r_[0, 0, 0], name='Sphere'):
    """Create sphere."""
    """radius r, position pos, name"""
    sphere = a.addObject('PartDesign::AdditiveSphere', name)
    sphere.Radius = r
    sphere.Placement = App.Placement(App.Vector(pos), App.Rotation(App.Vector(axis), angle), App.Vector(center))
    return sphere


def cone(r1=2, r2=4, h=10, pos=r_[0, 0, 0], axis=r_[0, 0, 1], angle=0, center=r_[0, 0, 0], name='Cone'):
    """Create cone."""
    """radius r1, r2, height h, position pos, name"""
    cone = a.addObject('PartDesign::AdditiveCone', name)
    cone.Radius1 = r1
    cone.Radius2 = r2
    cone.Height = h
    cone.Placement = App.Placement(App.Vector(pos), App.Rotation(App.Vector(axis), angle), App.Vector(center))
    return cone


def wedge(xmin=0, ymin=0, zmin=0, x2min=0, z2min=0, xmax=10, ymax=10, zmax=10, x2max=0, z2max=10,
          pos=r_[0, 0, 0], axis=r_[1, 0, 0], angle=-90, center=r_[0, 0, 0], name='Wedge'):
    """Create a wedge part."""
    """radius r1, r2, height h, position pos, name"""
    wedge = a.addObject('PartDesign::AdditiveWedge', name)
    wedge.Xmin = xmin
    wedge.Ymin = ymin
    wedge.Zmin = zmin
    wedge.X2min = x2min
    wedge.Z2min = z2min
    wedge.Xmax = xmax
    wedge.Ymax = ymax
    wedge.Zmax = zmax
    wedge.X2max = x2max
    wedge.Z2max = z2max
    wedge.Placement = App.Placement(App.Vector(pos), App.Rotation(App.Vector(axis), angle), App.Vector(center))
    return wedge


def body(name='Body'):
    """Create new Body."""
    body = a.addObject('PartDesign::Body', name)
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(body)
    return body


def angles(x, vec):
    """Calculate angles of edges to a given vector."""
    edges = x.Shape.Edges
    vec = vec / mag(vec)
    v_edge = [diff([(v.X, v.Y, v.Z) for v in e.Vertexes], axis=0) / e.Length for e in edges]
    corr = array(v_edge).dot(array(vec)).T[0]
    # angles = arccos(corr) * 180 / pi
    return corr


def fillet(body, r=1, edge_list=[], name='Fillet'):
    """Create Fillet."""
    tip = body.Tip
    fillet = body.newObject('PartDesign::Fillet', name)
    fillet.Base = tip, edge_list
    Gui.Selection.clearSelection()
    tip.ViewObject.hide()
    a.recompute()
    g.setEdit(name, 0)
    Gui.Selection.clearSelection()
    fillet.ViewObject.DisplayMode = body.ViewObject.DisplayMode
    fillet.Radius = r
    g.resetEdit()


def multifuse(objs, name='multifuse', a=a, g=g):
    """Fuse multiple parts."""
    part = a.addObject('Part::MultiFuse', name)
    part.Shapes = objs
    return part


def multicommon(objs, name='multicommon', a=a, g=g):
    """Intersect multiple parts."""
    part = a.addObject('Part::MultiCommon', name)
    # part.Shapes = [objs[0], objs[1:]]
    part.Shapes = objs
    return part


def multicut(obj_a, obj_b, name='multicut', a=a, g=g):
    """Difference of multiple parts."""
    if iterable(obj_b):
        cutting_obj = multifuse(obj_b, 'fused_parts_to_cutoff')
    part = a.addObject('Part::Cut', name)
    part.Base = obj_a
    part.Tool = cutting_obj
    return part


# fuse(a.netpot, rays, name='rays')

show_fan_cap        = 1
show_pcb            = 1
show_tube_holder    = 0
show_optics_holder  = 0
show_fan            = 0
show_fan_cover      = 0
show_ground_plate   = 0
show_support        = 0


line_width = 0.8
wall_thickness = 2 * line_width
layer_height = 0.12
board_width = 80
rTube = 25.7/2
dTubeHolderWall = 1.6
rTubeHolder = rTube + dTubeHolderWall

# ===================== FAN CAP ==========================
w_fan = 80
# hFanCap = 10
# dFanCap = 2
# hInner = 10
# rOuterHole = 4 / 2
# screwBorder = 1

# ======================= CAP ============================
rCapOutside = 180
oOutside = rCapOutside - 90
d_Cap = 2
h_Cap = 40
oInsideWallxy = 300
oInsideWallz = 50
rCapInside = sqrt(oInsideWallz**2 + (oInsideWallxy + w_fan / 2)**2) + 6
oInsideTopxy = 60
oInsideTopz = 180
rCapInsideTop = sqrt((oInsideTopz + h_Cap)**2 + (oInsideTopxy)**2)
# xConnectors = -14
board_thickness = 1.6

if show_fan_cap:
    body('FanCap')
    for k in range(5):
        pos = (oOutside + w_fan / 2) * r_[cos(k * pi / 2), sin(k * pi / 2), 0]
        sphere(rCapOutside, pos, name='Sphere' + str(k))
    a.Sphere4.Placement.Base = (0, 0, -rCapOutside + h_Cap)

    box(size=2 * rCapOutside * r_[1, 1, 1], pos=rCapOutside * r_[-1, -1, 0], name='CapUpperHalf')
    common(a.FanCap, [a.CapUpperHalf, a.Sphere0, a.Sphere1, a.Sphere2, a.Sphere3, a.Sphere4], name='CapHull')

    body('FanCapInner')
    for k in range(5):
        pos = (oOutside + w_fan / 2) * r_[cos(k * pi / 2), sin(k * pi / 2), 0]
        sphere(rCapOutside - wall_thickness, pos, name='SphereInner' + str(k))
        sphere(rCapOutside - wall_thickness + 0.1, pos, name='SphereEnvelope' + str(k))
    a.SphereInner4.Placement.Base = (0, 0, -rCapOutside + h_Cap)
    a.SphereEnvelope4.Placement.Base = (0, 0, -rCapOutside + h_Cap)

    # h_cone = h_Cap - d_Cap
    # cone(r1=150, r2=rTubeHolder, h=h_cone, pos=r_[0, 0, 0], name='CapCone')

    common(a.FanCapInner, [a.SphereInner0, a.SphereInner1, a.SphereInner2, a.SphereInner3, a.SphereInner4], name='MainSpace')
    cut(a.FanCap, a.FanCapInner)

    # round the edges outside
    edge_list = ["Edge16", "Edge6", "Edge7", "Edge8", "Edge14", "Edge10", "Edge1", "Edge2", "Edge5"]
    fillet(a.FanCap, r=5.0, edge_list=edge_list, name='FielehCapOuter')

    # round the edges inside
    edge_list = ["Edge62", "Edge60", "Edge55", "Edge53", "Edge59", "Edge58", "Edge54", "Edge56", "Edge57"]
    fillet(a.FanCap, r=5.0 - wall_thickness, edge_list=edge_list, name='FielehCapInner')

    # cutout for tube holder
    cylinder(r=rTubeHolder, h=50, name='TubeHole')
    cone(r1=43.6, r2=8, h=50)

    # ------------- Screws ---------------------
    r_screw_hole = 3 / 2
    r_screw_tube = r_screw_hole + 3.1 * line_width
    for k in range(4):
        phi = (k + 0.5) * pi / 2
        pos = 72 / 2 * sqrt(2) * r_[cos(phi), sin(phi), 0] + r_[0, 0, board_thickness+layer_height]
        cylinder(r=r_screw_tube, h=30.8, pos=pos, name='ScrewTube' + str(k))
        cylinder(r=r_screw_hole, h=29.8, pos=pos, name='ScrewHole' + str(k))

    # ------------- Support ---------------------
    box(size=r_[wall_thickness, 100, 40], pos=r_[15, -50, 0], name='Support0')
    box(size=r_[wall_thickness, 100, 40], pos=r_[-15 - wall_thickness, -50, 0], name='Support1')
    box(size=r_[100, wall_thickness, 40], pos=r_[-50, 15, 0], name='Support2')
    box(size=r_[100, wall_thickness, 40], pos=r_[-50, -15 - wall_thickness, 0], name='Support3')

    for k in range(4):
        phi_deg = k * 90 + 45
        phi_rad = phi_deg * pi / 180
        pos = 72 / 2 * sqrt(2) * r_[cos(phi_rad), sin(phi_rad), 0] + r_[-wall_thickness / 2, 0, board_thickness+layer_height]
        box(size=r_[wall_thickness, 10, 40], pos=pos, center=r_[wall_thickness / 2, 0, 0], angle=phi_deg-45-90, name='TubeSupport' + str(2*k))
        box(size=r_[wall_thickness, 10, 40], pos=pos, center=r_[wall_thickness / 2, 0, 0], angle=phi_deg+45-90, name='TubeSupport' + str(2*k + 1))
    box(size=r_[board_width, board_width, board_thickness], pos=r_[-board_width / 2, -board_width / 2, 0], name='BoardCutout')

    # ----------- Connectors -----------------------
    size_connector_box = r_[14, 70, 20]
    box(size=size_connector_box, pos=r_[-(38 + 20), -size_connector_box[1]/2, 0], name='ConnectorBox')
    wedge(xmin=0, ymin=0, zmin=-35, x2min=0, z2min=-35, xmax=10, ymax=10, zmax=35, x2max=0, z2max=35,
          pos=r_[-54, 0, 0], name='ConnectorBoxSupport')

    multifuse([a.Support0, a.Support1, a.Support2, a.Support3,
               a.TubeSupport0, a.TubeSupport1, a.TubeSupport2, a.TubeSupport3, a.TubeSupport4, a.TubeSupport5, a.TubeSupport6, a.TubeSupport7,
               a.ScrewTube0, a.ScrewTube1, a.ScrewTube2, a.ScrewTube3,
               a.ConnectorBox, a.ConnectorBoxSupport], 'CapInnerPartsRaw')

    box(size=r_[2*size_connector_box[0], 12.90, 11.50],
        pos=r_[-(38 + 20), -29.2, board_thickness-0.3], name='USBConnectorBoxCutout')
    box(size=r_[3*size_connector_box[0], 9.50, 11.50],
        pos=r_[-(38 + 20), -11.8, board_thickness-0.3], name='DCConnectorBoxCutout')
    cylinder(r=11.6/2, h=16, pos=r_[-(38 + 20), 13, 10], axis=r_[0, 1, 0], angle=90, name='PumpConnectorCylinderCutout1')
    cylinder(r=16/2, h=20, pos=r_[-68, 13, 10], axis=r_[0, 1, 0], angle=90, name='PumpConnectorCylinderCutout2')
    connector_cutout = [a.USBConnectorBoxCutout, a.DCConnectorBoxCutout, a.PumpConnectorCylinderCutout1, a.PumpConnectorCylinderCutout2]

    cut(a.FanCap, connector_cutout + [a.TubeHole], 'FanCapCutout')
    # multicommon([a.SphereInner0, a.SphereInner1, a.SphereInner2, a.SphereInner3, a.SphereInner4], 'CapEnvelope')
    # multicommon([a.Sphere0, a.Sphere1, a.Sphere2, a.Sphere3, a.Sphere4], 'CapEnvelope')
    multicommon([a.SphereEnvelope0, a.SphereEnvelope1, a.SphereEnvelope2, a.SphereEnvelope3, a.SphereEnvelope4], 'CapEnvelope')
    # edge_list = ["Edge2", "Edge5", "Edge7", "Edge8", "Edge9"]
    # fillet(a.FanCapInner, r=6.0, edge_list=edge_list, name='CapEnvelope')

    multicommon([a.CapEnvelope, a.CapInnerPartsRaw], 'CapInnerParts')
    multicut(a.CapInnerParts, [a.Cone, a.BoardCutout, a.ScrewHole0, a.ScrewHole1, a.ScrewHole2, a.ScrewHole3]+connector_cutout, name='InnerPartsCutOut')

    a.recompute()
    g.FanCap.Transparency = 50


mesh_path = '/home/boogieman/Dokumente/projekte/turbidostat/3d_models/'
mesh_offset = App.Placement(App.Vector(-40, -40, 0), App.Rotation(App.Vector(0, 0, 1), 0))
# ==================== PCB ============================
if show_pcb:
    body('PCB')
    g.ActiveView.setActiveObject('pdbody', a.PCB)
    FreeCADGui.insert(u"/home/boogieman/Dokumente/projekte/turbidostat/3d_models/pcb.wrl", "Turbidostat")
    a.pcb.Placement = App.Placement(App.Vector(140, -60, board_thickness/2), App.Rotation(App.Vector(0, 0, 1), 180))


## // ==================== TUBE HOLDER ============================
hTubeHolder = 90
hTubeHolderWindow = hTubeHolder-20-35
rTube = 25.7/2
dTubeHolderWall = 1.6
rTubeHolder = rTube + dTubeHolderWall
excentricity = 1.5
RimWidth = 8
rTubeHolderRim = rTubeHolder+RimWidth
rTubeHolderWindow = rTubeHolder/2
zOpticsHolder = 11
hOpticsHolder = 13
hMount = 7
rBeamPath = 3
dWindowPane = 2
wWindowPane = 8

if show_tube_holder:
    body('TubeHolder')
    # Mesh.insert(mesh_path + 'tubeholder.stl', 'Turbidostat')
    # a.tubeholder.Placement = App.Placement(App.Vector(-40, -40, +1.6), App.Rotation(App.Vector(0, 0, 1), 0))

    
#     color("SlateGray")
#     translate([0, 0, 0.1*explosion])
#     difference() {
#         union() {
            
#             // main cylinder
#             translate([wFan/2, wFan/2, 0])
#             // cylinder(h=hTubeHolder, r=rTubeHolder+ext, center=true);
#             // slightliy eliptical to hold the tube
#             elliptic_cylinder(h=hTubeHolder, a1=rTubeHolder, b1=rTubeHolder,
#                                             a2=rTubeHolder + excentricity/2, b2=rTubeHolder - excentricity/2,
#                                             center=false);
        
#             // rim
#             translate([wFan/2, wFan/2, -hMount/2 + zOpticsHolder])
#             cylinder(h=hMount, r1=rTubeHolder, r2=rTubeHolderRim, center=true);

#             // base
#             translate([wFan/2, wFan/2, zOpticsHolder/2-eps])
#             cube([2*rTubeHolder, 2*rTubeHolder, zOpticsHolder], center=true);

#             // pocket for window pane
#             translate([wFan/2, wFan/2, zOpticsHolder+hOpticsHolder/2-eps])
#             rotate([0, 0, 45]) 
#             cube([hOpticsHolder, 2*(rTubeHolder+dWindowPane), hOpticsHolder], center=true);
#         }

#         removeFrame = 1;
#         // pocket for window pane cutout - laser/sensor B side
#         translate([wFan/2, wFan/2, zOpticsHolder+hOpticsHolder/2-eps])
#         rotate([0, 0, 45]) 
#         translate([0, rTubeHolder+dWindowPane/2-0.3+removeFrame/2, 0])
#         #cube([wWindowPane+0.4, dWindowPane+removeFrame, hOpticsHolder], center=true);

#         // pocket for window pane cutout - Sensor A side
#         translate([wFan/2, wFan/2, zOpticsHolder+hOpticsHolder/2-eps])
#         rotate([0, 0, -(90+45)]) 
#         translate([0, rTubeHolder+dWindowPane/2-0.3+removeFrame/2, 0])
#         #cube([wWindowPane+0.4, dWindowPane+removeFrame, hOpticsHolder], center=true);

#         // // push-out-hole for window B
#         // translate([wFan/2, wFan/2, 0])
#         // rotate([0, 0, 45]) 
#         // translate([0, rTubeHolder+6*ext, 0.2 -2*eps])
#         // cylinder(h=zOpticsHolder+hOpticsHolder/2, r=dWindowPane/2, center=false, $fn=20);

#         // // push-out-hole for window A
#         // translate([wFan/2, wFan/2, 0])
#         // rotate([0, 0, -(90+45)]) 
#         // translate([0, rTubeHolder+6*ext, 0.2 -2*eps])
#         // cylinder(h=zOpticsHolder+hOpticsHolder/2, r=dWindowPane/2, center=false, $fn=20);

#         // cutout for arduino
#         // translate([wFan/2, wFan/2, hTubeHolder/2+2])
#         cube([wFan, +wFan/2 - rTubeHolder-0.8, hTubeHolder/2]);

#         // space for tube
#         translate([wFan/2, wFan/2, 2 + hCone-eps])
#         elliptic_cylinder(h=hTubeHolder - hCone, 
#             a1=rTube, b1=rTube,
#             a2=rTube + excentricity/2, b2=rTube - excentricity/2);
#         // cylinder(h=hTubeHolder, r=rTube+4*ext, center=true);

#         // space for tube - conical part
#         hCone = 2;
#         rConeUpper = rTube;
#         rConeLower = rTube  - 0.15;
#         translate([wFan/2, wFan/2, 2])
#         cylinder(h=hCone, r1=rConeLower , r2=rConeUpper, center=false);
        
#         // Windows
#         translate([wFan/2-1.5*rTube, wFan/2, hTubeHolder-10 -hTubeHolderWindow/2])
#         hull(){ 
#             translate([0, 0, hTubeHolderWindow/2])
#             rotate([0, 90, 0])
#             cylinder(h=3*rTube, r=rTubeHolderWindow/4, center=false);

#             rotate([90, 0, 90])
#             rounded_box(15, hTubeHolderWindow, 3*rTube, rTubeHolderWindow, center=true);
#         }

#         // cutout for beampath
#         translate([wFan/2, wFan/2, zOpticsHolder+hOpticsHolder/2])
#         rotate([90, 0, 45])
#         cylinder(h=hTubeHolder, r=rBeamPath, center=true);

#         // holes for screws (ears)
#         translate([wFan/2, wFan/2, zOpticsHolder+hOpticsHolder/2])
#         union() {
#             translate([0, rOpticsHolder+2.8, -hOpticsHolder/2+dEars/2])
#             cylinder(h=8*dEars, r=1, center=true);
#             translate([rOpticsHolder+2.8, 0, -hOpticsHolder/2+dEars/2])
#             cylinder(h=8*dEars, r=1, center=true);
#             rotate([0, 0, 30]) 
#             translate([-rOpticsHolder-2.8, 0, -hOpticsHolder/2+dEars/2])
#             cylinder(h=8*dEars, r=1, center=true);
#         }

#         // holes for screws (plate)
#         translate([wFan/2, wFan/2, 0])
#         union() {
#             for( x=(rTubeHolder-2.5)*[-1, +1] ){
#                 for( y=(rTubeHolder-2.5)*[-1, +1]){
#                     translate([x, y, 0])
#                     cylinder(h=8*dEars, r=1, center=true);
#                 }
#             }
#         }
#     }
# }

# ==================== OPTICS HOLDER ============================
if show_optics_holder:
    body('OpticsHolder')
    Mesh.insert(mesh_path + 'optics_holder.stl', 'Turbidostat')
    a.optics_holder.Placement = a.tubeholder.Placement


# ==================== FAN ============================
h_fan = 15
w_fan = 80
r_fan_edge = 4
h_magnet_clearance = 6
h_fan_cover = h_fan + h_magnet_clearance + 3
if show_fan:
    body('Fan')
    g.ActiveView.setActiveObject('pdbody', a.Fan)
    box(size=r_[w_fan, w_fan, h_fan], pos=r_[-w_fan/2, -w_fan/2, -h_fan - h_magnet_clearance], name='FanBox')
    a.Fan.addObject(a.FanBox)
    edge_list = ["Edge1", "Edge5", "Edge3", "Edge7"]
    fillet(a.Fan, r=4.0, edge_list=edge_list, name='FanFillet')

    cylinder(r=38, h=40, pos=r_[0, 0, -h_fan_cover + layer_height], name='FanHole')
    cut(a.Fan, a.FanHole)

# ==================== FAN COVER =========================

if show_fan_cover:
    body('FanCover')
    g.ActiveView.setActiveObject('pdbody', a.FanCover)
    for k in range(4):
        pos = (oOutside + w_fan / 2) * r_[cos(k * pi / 2), sin(k * pi / 2), 0] - r_[0, 0, h_fan_cover]
        cylinder(rCapOutside, h=h_fan_cover, pos=pos, name='Cylinder' + str(k))

    # box(size=2 * rCapOutside * r_[1, 1, 1], pos=rCapOutside * r_[-1, -1, 0], name='CapUpperHalf')
    common(a.FanCover, [a.Cylinder0, a.Cylinder1, a.Cylinder2, a.Cylinder3], name='FanCoverHull')
    body('FanCoverInner')
    for k in range(4):
        pos = (oOutside + w_fan / 2) * r_[cos(k * pi / 2), sin(k * pi / 2), 0] - r_[0, 0, h_fan_cover]
        cylinder(rCapOutside-wall_thickness, h=h_fan_cover, pos=pos, name='CylinderInner' + str(k))

    common(a.FanCoverInner, [a.CylinderInner0, a.CylinderInner1, a.CylinderInner2, a.CylinderInner3], name='FanCoverSpace')
    cut(a.FanCover, a.FanCoverInner)

    edge_list = ["Edge2", "Edge14", "Edge4", "Edge25", ]
    fillet(a.FanCover, r=5.0, edge_list=edge_list, name='FielehFanCoverOuter')

    edge_list = ["Edge38", "Edge39", "Edge41", "Edge40", ]
    fillet(a.FanCover, r=5.0 - wall_thickness, edge_list=edge_list, name='FielehFanCoverInner')

    # a.addObject('Part::MultiFuse', 'CapInnerPartsRaw')
    width = 96
    base_plate_thickness = 3
    h = h_fan_cover - base_plate_thickness
    box(size=r_[wall_thickness, width, h], pos=r_[15, -width/2, -h], name='FanCoverSpacer0')
    box(size=r_[wall_thickness, width, h], pos=r_[-15 - wall_thickness, -width/2, -h], name='FanCoverSpacer1')
    box(size=r_[width, wall_thickness, h], pos=r_[-width/2, 15, -h], name='FanCoverSpacer2')
    box(size=r_[width, wall_thickness, h], pos=r_[-width/2, -15 - wall_thickness, -h], name='FanCoverSpacer3')

    fuse(a.FanCover, [a.FanCoverSpacer0, a.FanCoverSpacer1, a.FanCoverSpacer2, a.FanCoverSpacer3, ], name='FanCoverSpacer')

    box(size=r_[w_fan, w_fan, h_fan_cover], pos=r_[-w_fan/2, -w_fan/2, -h_fan_cover + layer_height], name='FanSpace')
    cut(a.FanCover, a.FanSpace)

    g.FanCover.Transparency = 50

# ==================== GROUND PLATE =========================
if show_ground_plate:
    body('GroundPlate')
    g.ActiveView.setActiveObject('pdbody', a.GroundPlate)
    h_ground_plate = 2
    # body('FanCoverInner')
    for k in range(4):
        pos = (oOutside + w_fan / 2) * r_[cos(k * pi / 2), sin(k * pi / 2), 0] - r_[0, 0, h_fan_cover]
        cylinder(rCapOutside-wall_thickness, h=h_ground_plate, pos=pos, name='GPCylinderInner' + str(k))

    common(a.GroundPlate, [a.GPCylinderInner0, a.GPCylinderInner1, a.GPCylinderInner2, a.GPCylinderInner3], name='GroundPlateBase')
    edge_list = ["Edge2", "Edge9", "Edge4", "Edge15"]
    fillet(a.GroundPlate, r=4.0, edge_list=edge_list, name='GroundPlateFillet')

    g.GroundPlate.Transparency = 50

# ==================== SUPPORT STRUCTURE =========================
support_clearance = 2*layer_height
if show_support:
    body('Supports')
    g.ActiveView.setActiveObject('pdbody', a.Supports)
    width = 91
    w_support_base = w_fan+4
    box(size=r_[w_support_base, w_support_base, layer_height/2], pos=r_[-w_support_base/2, -w_support_base/2, -h_fan_cover], name='FanCoverSupport0')
    box(size=r_[4*wall_thickness, width, base_plate_thickness - 3*layer_height], pos=r_[15, -width/2, -h_fan_cover], name='FanCoverSupport1')
    box(size=r_[4*wall_thickness, width, base_plate_thickness - 3*layer_height], pos=r_[-15 - wall_thickness, -width/2, -h_fan_cover], name='FanCoverSupport2')
    box(size=r_[width, 4*wall_thickness, base_plate_thickness - 3*layer_height], pos=r_[-width/2, 15, -h_fan_cover], name='FanCoverSupport3')
    box(size=r_[width, 4*wall_thickness, base_plate_thickness - 3*layer_height], pos=r_[-width/2, -15 - wall_thickness, -h_fan_cover], name='FanCoverSupport4')
    for k in range(4):
        r1 = r_screw_tube
        r2 = r_screw_tube - 2*line_width
        h = h_fan_cover + board_thickness - support_clearance
        phi_deg = k * 90 + 45
        phi_rad = phi_deg * pi / 180
        pos = 72 / 2 * sqrt(2) * r_[cos(phi_rad), sin(phi_rad), 0] + r_[0, 0, -h_fan_cover]
        cylinder(r=r1, h=h, pos=pos, name='SupportCylinder' + str(k))
        cylinder(r=1.6*r1, h=1, pos=pos, name='SupportCylinderBase' + str(k))
        cylinder(r=r2, h=h, pos=pos, name='SupportCylinderHole' + str(k))
        box(size=r_[wall_thickness, 10, 5], pos=pos-r_[wall_thickness / 2, 0, -4], center=r_[wall_thickness / 2, 0, 0], angle=phi_deg-90, name='SupportCylinderMount' + str(k))
        # box(size=r_[wall_thickness, 8, 20], pos=pos-r_[wall_thickness / 2, 0, 0], center=r_[wall_thickness / 2, 0, 0], angle=phi_deg+45-90, name='SupportCylinderMount' + str(2*k + 1))
        # box(size=r_[wall_thickness, 8, 20], pos=pos-r_[wall_thickness / 2, 0, 0], center=r_[wall_thickness / 2, 0, 0], angle=phi_deg-45-90, name='SupportCylinderMount' + str(2*k))

    fuse(a.Supports, [a.FanCoverSupport0, a.FanCoverSupport1, a.FanCoverSupport2, a.FanCoverSupport3, a.FanCoverSupport4], name='SupportsFuse')
    cut(a.Supports, a.FanSpace)
    fuse(a.Supports, [a.SupportCylinder0, a.SupportCylinder1, a.SupportCylinder2, a.SupportCylinder3,
                      a.SupportCylinderBase0, a.SupportCylinderBase1, a.SupportCylinderBase2, a.SupportCylinderBase3,
                      a.SupportCylinderMount0, a.SupportCylinderMount1, a.SupportCylinderMount2, a.SupportCylinderMount3],
         name='SupportsFuse')
    cut(a.Supports, [a.SupportCylinderHole0, a.SupportCylinderHole1, a.SupportCylinderHole2, a.SupportCylinderHole3])


# def export(objs=[a.FanCap, a.InnerPartsCutOut, a.FanCover, a.Supports]):
#     """Export STL file."""
#     g.FanCover.Deviation = 0.02
#     g.FanCap.Deviation = 0.02
#     Mesh.export(objs, u"/home/boogieman/Dokumente/projekte/turbidostat/3d_models/turbidostat_freecad3.stl")

# def init_sketch(name='Sketch'):
#     """Init sketch."""
#     sketch = a.Supports.newObject('Sketcher::SketchObject', name)
#     sketch.Support = (a.XY_Plane004, [''])
#     sketch.MapMode = 'FlatFace'
#     a.recompute()
#     g.setEdit(name)
#     Gui.activateWorkbench('SketcherWorkbench')
#     # import PartDesignGui
#     active_sketch = a.getObject(name)
#     tv = Show.TempoVis(App.ActiveDocument)
#     if active_sketch.ViewObject.HideDependent:
#         objs = tv.get_all_dependent(active_sketch)
#         objs = filter(lambda x: not x.TypeId.startswith("TechDraw::"), objs)
#         objs = filter(lambda x: not x.TypeId.startswith("Drawing::"), objs)
#         tv.hide(objs)
#     if active_sketch.ViewObject.ShowSupport:
#         tv.show([ref[0] for ref in active_sketch.Support if not ref[0].isDerivedFrom("PartDesign::Plane")])
#     if active_sketch.ViewObject.ShowLinks:
#         tv.show([ref[0] for ref in active_sketch.ExternalGeometry])
#     tv.hide(active_sketch)
#     active_sketch.ViewObject.TempoVis = tv
#     del(tv)

#     active_sketch = a.getObject(name)
#     if active_sketch.ViewObject.RestoreCamera:
#         active_sketch.ViewObject.TempoVis.saveCamera()


# def end_sketch():
#     """."""
#     Gui.getDocument('Turbidostat').resetEdit()
#     sketch = App.ActiveDocument.getObject('Sketch')
#     tv = sketch.ViewObject.TempoVis
#     if tv:
#         tv.restore()
#     sketch.ViewObject.TempoVis = None
#     del(tv)

Gui.activateWorkbench('PartDesignWorkbench')

# g.ActiveView.setActiveObject('pdbody', a.Supports)
# init_sketch()
# a.Sketch.addGeometry(Part.Circle(App.Vector(34.000000, 36.517078, 0), App.Vector(0, 0, 1), 3.916080), False)
# end_sketch()

# g.ActiveView.setActiveObject('pdbody', a.FanCap)
a.recompute()
# Gui.SendMsgToActiveView('ViewFit')


# # FLAT NETPOT
# n_rays = 24
# rays = []
# body('netpot')
# for k in range(n_rays/2):
#     rays.append(box(size=r_[200, 2, 1], center=r_[100, 1, 0], angle=360 / n_rays * k, name='ray'+str(k)))


# # find edges. How to use with PartDesign fillet???
# edges = array(a.FanCap.Shape.Edges)
# ix_vertical_edges = abs(angles(a.FanCap, (0, 0, 1))) > 0.9
# ix_corner_edges = array([abs(e.Vertexes[0].Y) for e in edges]) > 10
# ix_edges = ix_vertical_edges & ix_corner_edges
#
# s=fg.Selection.getSelectionEx()[0]
# s.SubElementNames
