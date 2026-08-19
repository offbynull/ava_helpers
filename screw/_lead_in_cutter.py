import FreeCAD as App

from screw.cone_frustum_parameters import ConeFrustumParameters

_BUFFER = 10 * App.Units.MilliMetre


def cut_lead_in_lower(
        doc: App.Document,
        body: App.DocumentObject,
        minor_cone: ConeFrustumParameters,
        chamfer_cone_radius_lower: App.Units.Quantity,
        chamfer_radius_distance: App.Units.Quantity,
        thread_profile_width: App.Units.Quantity,
):
    if minor_cone.angle != 0:
        minor_cone_height_at_chamfer_end = minor_cone.bottom_height + chamfer_radius_distance
        minor_cone_radius_at_chamfer_height = minor_cone.radius_at_height(minor_cone_height_at_chamfer_end)
    else:
        minor_cone_radius_at_chamfer_height = minor_cone.bottom_radius
    cut_body = doc.addObject('PartDesign::Body', 'Lower Lead-in Cut Body')
    outer_cone = cut_body.newObject('PartDesign::AdditiveCone', 'Lower Lead-in Outer Cone')
    outer_cone.Radius1 = minor_cone.bottom_radius + thread_profile_width + _BUFFER
    outer_cone.Radius2 = minor_cone_radius_at_chamfer_height + thread_profile_width + _BUFFER
    outer_cone.Height = chamfer_radius_distance
    outer_cone.Angle = 360 * App.Units.Degree
    inner_cone = cut_body.newObject('PartDesign::SubtractiveCone', 'Lower Lead-in Inner Cone')
    inner_cone.Radius1 = chamfer_cone_radius_lower
    inner_cone.Radius2 = minor_cone_radius_at_chamfer_height + thread_profile_width
    inner_cone.Height = chamfer_radius_distance
    inner_cone.Angle = 360 * App.Units.Degree
    boolean_cut = body.newObject('PartDesign::Boolean', 'Lower Lead-in Lead-in Cut')
    boolean_cut.addObjects([cut_body, ])
    boolean_cut.setObjects([cut_body, ])
    boolean_cut.Type = 1
    return boolean_cut


def cut_lead_in_upper(
        doc: App.Document,
        body: App.DocumentObject,
        minor_cone: ConeFrustumParameters,
        chamfer_cone_radius_lower: App.Units.Quantity,
        chamfer_radius_distance: App.Units.Quantity,
        thread_profile_width: App.Units.Quantity,
):
    if minor_cone.angle != 0:
        minor_cone_height_at_chamfer_end = minor_cone.top_height + chamfer_radius_distance
        minor_cone_radius_at_chamfer_height = minor_cone.radius_at_height(minor_cone_height_at_chamfer_end)
    else:
        minor_cone_radius_at_chamfer_height = minor_cone.top_radius
    cut_body = doc.addObject('PartDesign::Body', 'Upper Lead-in Cut Body')
    outer_cone = cut_body.newObject('PartDesign::AdditiveCylinder', 'Upper Lead-in Outer Cylinder')
    outer_cone.Radius = minor_cone_radius_at_chamfer_height + thread_profile_width + _BUFFER
    outer_cone.Height = chamfer_radius_distance
    outer_cone.Angle = 360 * App.Units.Degree
    inner_cone = cut_body.newObject('PartDesign::SubtractiveCone', 'Upper Lead-in Inner Cone')
    inner_cone.Radius1 = chamfer_cone_radius_lower
    inner_cone.Radius2 = minor_cone_radius_at_chamfer_height + thread_profile_width
    inner_cone.Height = chamfer_radius_distance
    inner_cone.Angle = 360 * App.Units.Degree
    boolean_cut = body.newObject('PartDesign::Boolean', 'Upper Lead-in Lead-in Cut')
    boolean_cut.addObjects([cut_body, ])
    boolean_cut.setObjects([cut_body, ])
    boolean_cut.Type = 1
    boolean_cut.OutList[1].Placement = App.Placement(
        App.Vector(0, 0, minor_cone.distance_between_radiuses.Value),
        App.Rotation(App.Vector(0, 1, 0), 180)
    )
    return boolean_cut
