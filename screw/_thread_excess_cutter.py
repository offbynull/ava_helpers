import FreeCAD as App

from screw.geometries.cone_frustum import ConeFrustum

_BUFFER = 10 * App.Units.MilliMetre


def cut_excess_thread_lower(
        body: App.DocumentObject,
        minor_cone: ConeFrustum,
        cut_distance: App.Units.Quantity,
        thread_profile_x_protrusion_distance: App.Units.Quantity,
):
    cut_cone_radius_lower = minor_cone.bottom_radius + thread_profile_x_protrusion_distance + _BUFFER
    cut_cone_radius_upper = minor_cone.bottom_radius + thread_profile_x_protrusion_distance + _BUFFER
    cut_cone_radius_distance = cut_distance
    cut_cone = body.newObject('PartDesign::SubtractiveCone', 'Lower Excess Thread Trim')
    cut_cone.Radius1 = cut_cone_radius_lower
    cut_cone.Radius2 = cut_cone_radius_upper
    cut_cone.Height = cut_cone_radius_distance
    cut_cone.Placement = App.Placement(
        App.Vector(0, 0, -cut_distance.Value),
        App.Rotation(App.Vector(0, 0, 1), 0)
    )
    return cut_cone

def cut_excess_thread_upper(
        body: App.DocumentObject,
        minor_cone: ConeFrustum,
        cut_distance: App.Units.Quantity,
        thread_profile_x_protrusion_distance: App.Units.Quantity,
):
    cut_cone_radius_lower = minor_cone.top_radius + thread_profile_x_protrusion_distance + _BUFFER
    cut_cone_radius_upper = minor_cone.top_radius + thread_profile_x_protrusion_distance + _BUFFER
    cut_cone_radius_distance = cut_distance
    cut_cone = body.newObject('PartDesign::SubtractiveCone', 'Upper Excess Thread Trim')
    cut_cone.Radius1 = cut_cone_radius_lower
    cut_cone.Radius2 = cut_cone_radius_upper
    cut_cone.Height = cut_cone_radius_distance
    cut_cone.Placement = App.Placement(
        App.Vector(0, 0, minor_cone.distance_between_radiuses.Value),
        App.Rotation(App.Vector(0, 0, 1), 0)
    )
    return cut_cone
