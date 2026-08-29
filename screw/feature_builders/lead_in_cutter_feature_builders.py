import FreeCAD as App

from screw.geometries.cone_frustum import ConeFrustum
from screw.geometries.cylinder import Cylinder
from screw.thread_profile_extents import ThreadProfileExtents

_BUFFER = 10 * App.Units.MilliMetre


def build_bottom_lead_in_cutter_feature(
        doc: App.Document,
        body: App.DocumentObject,
        minor_shape: ConeFrustum | Cylinder,
        lead_in_radius_offset: App.Units.Quantity,
        lead_in_distance: App.Units.Quantity,
        thread_profile_extents: ThreadProfileExtents
):
    cut_body = doc.addObject('PartDesign::Body', 'Bottom Lead-in Cut Body')
    thread_protrusion = thread_profile_extents.beside_distance
    major_shape = minor_shape.widen(thread_protrusion)
    truncated_major_shape = major_shape \
        .with_distance_from_bottom(lead_in_distance) \
        .widen(_BUFFER)
    truncated_major_shape.create_partdesign_additive_cone(cut_body, 'Bottom Lead-in Outer Cone')
    if isinstance(minor_shape, ConeFrustum):
        chamfer_shape = major_shape \
            .with_distance_from_bottom(lead_in_distance) \
            .widen_bottom(lead_in_radius_offset)
    else:
        chamfer_shape = ConeFrustum(
            minor_shape.radius + lead_in_radius_offset,
            major_shape.radius,
            lead_in_distance
        )
    chamfer_shape.create_partdesign_subtractive_cone(cut_body, 'Bottom Lead-in Inner Cone')
    boolean_cut = body.newObject('PartDesign::Boolean', 'Bottom Lead-in Cut')
    boolean_cut.addObjects([cut_body, ])
    boolean_cut.setObjects([cut_body, ])
    boolean_cut.Type = 1
    return boolean_cut


def build_top_lead_in_cutter_feature(
        doc: App.Document,
        body: App.DocumentObject,
        minor_shape: ConeFrustum | Cylinder,
        lead_in_radius_offset: App.Units.Quantity,
        lead_in_distance: App.Units.Quantity,
        thread_profile_extents: ThreadProfileExtents
):
    cut_body = doc.addObject('PartDesign::Body', 'Top Lead-in Cut Body')
    thread_protrusion = thread_profile_extents.beside_distance
    major_shape = minor_shape.widen(thread_protrusion)
    truncated_major_shape = major_shape \
        .with_distance_from_top(lead_in_distance) \
        .widen(_BUFFER)
    truncated_major_shape.create_partdesign_additive_cone(cut_body, 'Top Lead-in Outer Cone')
    if isinstance(minor_shape, ConeFrustum):
        chamfer_shape = major_shape \
            .with_distance_from_top(lead_in_distance) \
            .widen_top(lead_in_radius_offset)
    else:
        chamfer_shape = ConeFrustum(
            major_shape.radius,
            minor_shape.radius + lead_in_radius_offset,
            lead_in_distance
        )
    chamfer_shape.create_partdesign_subtractive_cone(cut_body, 'Top Lead-in Inner Cone')
    boolean_cut = body.newObject('PartDesign::Boolean', 'Top Lead-in Cut')
    boolean_cut.addObjects([cut_body, ])
    boolean_cut.setObjects([cut_body, ])
    boolean_cut.Type = 1
    boolean_cut.OutList[1].Placement = App.Placement(
        App.Vector(0, 0, minor_shape.distance_between_radiuses.Value - lead_in_distance.Value),
        App.Rotation(App.Vector(0, 1, 0), 0)
    )
    return boolean_cut
