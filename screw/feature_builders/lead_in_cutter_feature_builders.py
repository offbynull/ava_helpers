import FreeCAD as App

from screw.geometries.cone_frustum import ConeFrustum, FeatureMode
from screw.lead_in_parameters import LeadInParameters
from screw.thread_profile_extents_set import ThreadProfileExtentsSet

FIX ME FIX ME FIX ME
FIX ME FIX ME FIX ME
FIX ME FIX ME FIX ME
FIX ME FIX ME FIX ME
FIX ME FIX ME FIX ME
FIX ME FIX ME FIX ME


_BUFFER = 10 * App.Units.MilliMetre


def build_bottom_lead_in_cutter_feature(
        doc: App.Document,
        body: App.DocumentObject,
        minor_cone: ConeFrustum,
        lead_in: LeadInParameters,
        thread_profile_extents_set: ThreadProfileExtentsSet
):
    cut_body = doc.addObject('PartDesign::Body', 'Bottom Lead-in Cut Body')
    max_thread_side_protrusion = thread_profile_extents_set.side_protrusion_distance(minor_cone)
    major_cone = minor_cone.widen(max_thread_side_protrusion + _BUFFER)
    truncated_major_cone = major_cone.shift_bottom(lead_in.distance_between_radiuses)
    truncated_major_cone.create_partdesign_additive_cone(cut_body, 'Bottom Lead-in Outer Cone')
    chamfer_cone = lead_in.apply_to_bottom(truncated_major_cone)
    chamfer_cone.create_partdesign_subtractive_cone(cut_body, 'Bottom Lead-in Inner Cone')
    boolean_cut = body.newObject('PartDesign::Boolean', 'Bottom Lead-in Cut')
    boolean_cut.addObjects([cut_body, ])
    boolean_cut.setObjects([cut_body, ])
    boolean_cut.Type = 1
    return boolean_cut


def build_top_lead_in_cutter_feature(
        doc: App.Document,
        body: App.DocumentObject,
        minor_cone: ConeFrustum,
        lead_in: LeadInParameters,
        thread_profile_extents_set: ThreadProfileExtentsSet
):
    cut_body = doc.addObject('PartDesign::Body', 'Top Lead-in Cut Body')
    max_thread_side_protrusion = thread_profile_extents_set.side_protrusion_distance(minor_cone)
    major_cone = minor_cone.widen(max_thread_side_protrusion + _BUFFER)
    truncated_major_cone = major_cone.shift_top(lead_in.distance_between_radiuses)
    truncated_major_cone.create_partdesign_additive_cone(cut_body, 'Top Lead-in Outer Cone')
    chamfer_cone = lead_in.apply_to_top(major_cone)
    chamfer_cone.create_partdesign_subtractive_cone(cut_body, 'Top Lead-in Inner Cone')
    boolean_cut = body.newObject('PartDesign::Boolean', 'Top Lead-in Cut')
    boolean_cut.addObjects([cut_body, ])
    boolean_cut.setObjects([cut_body, ])
    boolean_cut.Type = 1
    boolean_cut.OutList[1].Placement = App.Placement(
        App.Vector(0, 0, minor_cone.distance_between_radiuses.Value),
        App.Rotation(App.Vector(0, 1, 0), 180)
    )
    return boolean_cut