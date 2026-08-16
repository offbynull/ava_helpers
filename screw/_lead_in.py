from os import major

import FreeCAD as App

from screw._trigonometry import cone_radius_at_height, cone_height_at_radius, cone_frustum_to_angle


def _lead_in_cutter(
        doc: App.Document,
        body: App.DocumentObject,
        name: str,
        cone_radius_lower: App.Units.Quantity,
        cone_radius_upper: App.Units.Quantity,
        cone_radius_distance: App.Units.Quantity,
        chamfer_distance: App.Units.Quantity,
        chamfer_radius: App.Units.Quantity
):
    major_cone_angle = cone_frustum_to_angle(cone_radius_lower, cone_radius_upper, cone_radius_distance)
    if major_cone_angle != 0:
        major_cone_end_radius_height = cone_height_at_radius(major_cone_angle, cone_radius_lower)
        major_cone_chamfer_radius = cone_radius_at_height(major_cone_angle, major_cone_end_radius_height + chamfer_distance)
    else:
        major_cone_chamfer_radius = cone_radius_lower
    cut_body = doc.addObject('PartDesign::Body', f'{name} Body')
    outer_cone = cut_body.newObject('PartDesign::AdditiveCone', f'{name} Outer Cone')
    # Add a 5mm buffer because cone's smooth surface doesn't intersect well with additive helix's jagged helix projections
    outer_cone.Radius1 = cone_radius_lower + (5 * App.Units.MilliMetre)
    outer_cone.Radius2 = major_cone_chamfer_radius  + (5 * App.Units.MilliMetre)
    outer_cone.Height = chamfer_distance
    outer_cone.Angle = 360 * App.Units.Degree
    inner_cone = cut_body.newObject('PartDesign::SubtractiveCone', f'{name} Inner Cone')
    inner_cone.Radius1 = chamfer_radius
    inner_cone.Radius2 = major_cone_chamfer_radius
    inner_cone.Height = chamfer_distance
    inner_cone.Angle = 360 * App.Units.Degree
    boolean_cut = body.newObject('PartDesign::Boolean', f'{name} Lead-in Cut')
    boolean_cut.addObjects([cut_body, ])
    boolean_cut.setObjects([cut_body, ])
    boolean_cut.Type = 1
    return boolean_cut

def end_lead_in_cutter(
        doc: App.Document,
        body: App.DocumentObject,
        name: str,
        major_cone_end_radius: App.Units.Quantity,
        major_cone_head_radius: App.Units.Quantity,
        major_cone_radius_distance: App.Units.Quantity,
        lead_in_distance: App.Units.Quantity,
        lead_in_end_radius: App.Units.Quantity
):
    return _lead_in_cutter(
        doc,
        body,
        name,
        major_cone_end_radius,
        major_cone_head_radius,
        major_cone_radius_distance,
        lead_in_distance,
        lead_in_end_radius
    )


def head_lead_in_cutter(
        doc: App.Document,
        body: App.DocumentObject,
        name: str,
        major_cone_end_radius: App.Units.Quantity,
        major_cone_head_radius: App.Units.Quantity,
        major_cone_radius_distance: App.Units.Quantity,
        lead_in_distance: App.Units.Quantity,
        lead_in_end_radius: App.Units.Quantity
):
    ret = _lead_in_cutter(
        doc,
        body,
        name,
        major_cone_head_radius,
        major_cone_end_radius,
        major_cone_radius_distance,
        lead_in_distance,
        lead_in_end_radius
    )
    ret.OutList[1].Placement = App.Placement(
        App.Vector(0, 0, major_cone_radius_distance.Value),
        App.Rotation(App.Vector(0, 1, 0), 180)
    )
