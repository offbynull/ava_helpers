import FreeCAD as App

from screw.geometries.cone_frustum import ConeFrustum
from screw.geometries.cylinder import Cylinder
from screw.thread_profile_extents import ThreadProfileExtents


def build_thread_feature(
        doc: App.Document,
        body: App.DocumentObject,
        index: int,
        minor_shape: ConeFrustum | Cylinder,
        thread_profile_sketch: App.DocumentObject,
        thread_profile_extents: ThreadProfileExtents,
        thread_lead: App.Units.Quantity,
        thread_left_handed: bool
):
    helix = body.newObject('PartDesign::AdditiveHelix', f'Thread Helix {index}')
    helix.Profile = (thread_profile_sketch, ['', ])
    helix.ReferenceAxis = (thread_profile_sketch, ['V_Axis'])
    helix.Mode = 0
    helix.Pitch = thread_lead  # + (0.0001 * App.Units.MilliMetre)  # Need 0.0001mm or else the geometry breaks
    helix.Height = minor_shape.distance_between_radiuses + thread_profile_extents.underneath_distance  # Height is the height of the frustum + continuing further up until the bottom of the sketch touches the tip of the frustum
    helix.Angle = minor_shape.angle
    helix.LeftHanded = thread_left_handed
    helix.Reversed = 0
    return helix
