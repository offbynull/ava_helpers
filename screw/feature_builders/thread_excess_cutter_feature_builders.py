import FreeCAD as App

from screw.geometries.cone_frustum import ConeFrustum
from screw.geometries.cylinder import Cylinder
from screw.thread_profile_extents_set import ThreadProfileExtentsSet

_BUFFER = 10 * App.Units.MilliMetre


def build_bottom_thread_excess_cutter_feature(
        doc: App.Document,
        body: App.DocumentObject,
        minor_shape: ConeFrustum | Cylinder,
        thread_profile_extents_set: ThreadProfileExtentsSet
):
    max_thread_side_protrusion = thread_profile_extents_set.side_protrusion_distance(minor_shape)
    major_shape = minor_shape.widen(max_thread_side_protrusion)
    trim_shape = Cylinder(
        major_shape.bottom_radius + _BUFFER,
        thread_profile_extents_set.underneath_distance + _BUFFER
    )
    trim_shape_feature = trim_shape.create_partdesign_subtractive_cylinder(body, 'Bottom Excess Thread Trim')
    trim_shape_feature.Placement = App.Placement(
        App.Vector(0, 0, -trim_shape.distance_between_radiuses.Value),
        App.Rotation(App.Vector(0, 0, 1), 0)
    )
    return trim_shape_feature


def build_top_thread_excess_cutter_feature(
        doc: App.Document,
        body: App.DocumentObject,
        minor_shape: ConeFrustum | Cylinder,
        thread_profile_extents_set: ThreadProfileExtentsSet
):
    max_thread_side_protrusion = thread_profile_extents_set.side_protrusion_distance(minor_shape)
    major_shape = minor_shape.widen(max_thread_side_protrusion)
    trim_shape = Cylinder(
        major_shape.top_radius + _BUFFER,
        thread_profile_extents_set.height + _BUFFER
    )
    trim_shape_feature = trim_shape.create_partdesign_subtractive_cylinder(body, 'Top Excess Thread Trim')
    trim_shape_feature.Placement = App.Placement(
        App.Vector(0, 0, major_shape.distance_between_radiuses.Value),
        App.Rotation(App.Vector(0, 0, 1), 0)
    )
    return trim_shape_feature
