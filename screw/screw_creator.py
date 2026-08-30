import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui

from logger import warn
from screw.feature_builders.lead_in_cutter_feature_builders import build_bottom_lead_in_cutter_feature, \
    build_top_lead_in_cutter_feature
from screw.feature_builders.minor_shape_feature_builder import build_minor_cone_feature
from screw.feature_builders.stack_feature_builder import build_stack_feature
from screw.feature_builders.thread_excess_cutter_feature_builders import build_bottom_thread_excess_cutter_feature, \
    build_top_thread_excess_cutter_feature
from screw.feature_builders.thread_feature_builder import build_thread_feature
from screw.geometries.cone_frustum import ConeFrustum
from screw.geometries.cylinder import Cylinder
from screw.screw_form import ScrewForm
from screw.thread_profile_extents import ThreadProfileExtents
from screw.thread_profile_sketchers import square_profile_sketcher, triangle_profile_sketcher, \
    trapezoid_profile_sketcher
from screw.ui_components.tab_collection_widget import TabCollection


_THREAD_PROFILES = [
    triangle_profile_sketcher,
    square_profile_sketcher,
    trapezoid_profile_sketcher
]


def run(doc: App.Document) -> None:
    if doc is None:
        warn('AvaHelpersWorkbench: no active document.')
        return

    class ScrewCreateTaskPanel:
        def __init__(self):
            self.form = TabCollection(
                lambda i: (f'{i}', ScrewForm(_THREAD_PROFILES, self.preview, self.form)),
                self.preview
            )
            self.form.add()
            # self.form = ScrewForm(_THREAD_PROFILES, self.preview)

            doc.openTransaction('Create screw')
            self.preview()  # Initial launch

        def preview(self, *args):
            doc.abortTransaction()
            doc.openTransaction('Create screw')

            child_bodies = []
            for i, screw_form in enumerate(self.form.widgets()):
                name = screw_form.name
                body = doc.addObject('PartDesign::Body', name)

                # Surface parameters
                # ------------------
                if screw_form.cone_bottom_radius != screw_form.cone_top_radius:
                    minor_cone = ConeFrustum(
                        screw_form.cone_bottom_radius,
                        screw_form.cone_top_radius,
                        screw_form.cone_distance_between_radiuses
                    )
                else:
                    minor_cone = Cylinder(
                        screw_form.cone_bottom_radius,
                        screw_form.cone_distance_between_radiuses
                    )

                # Thread
                # ------
                thread_profile_extents = None
                if screw_form.threaded:
                    for i in range(0, screw_form.thread_starts):
                        plane = body.newObject('Part::DatumPlane', f'Thread Profile {i} Plane')
                        plane.AttachmentOffset = App.Placement(
                            App.Vector(0.0, 0.0, 0.0),
                            App.Rotation(0.0, i / screw_form.thread_starts * 360.0, 0.0)
                        )
                        plane.MapReversed = False
                        plane.AttachmentSupport = [(body.Origin, '')]
                        plane.MapMode = 'ObjectXZ'
                        plane.Visibility = False
                        sketch = body.newObject('Sketcher::SketchObject', f'Thread Profile {i}')
                        sketch.AttachmentSupport = plane, []
                        sketch.MapMode = 'FlatFace'
                        sketch.Visibility = False
                        # It's the same sketch being generated everytime, but on a different face. The extents should always
                        # be the same (or close enough, there may be rounding error). As such, the extents don't need to be
                        # overridden here but it also doesn't really matter if they are.
                        thread_profile_extents = screw_form.thread_profile_card.sketch(doc, sketch, minor_cone)
                        build_thread_feature(
                            doc,
                            body,
                            i,
                            minor_cone,
                            sketch,
                            thread_profile_extents,
                            screw_form.thread_lead,
                            screw_form.thread_left_handed
                        )

                # Surface generation
                # ------------------
                build_minor_cone_feature(doc, body, minor_cone)

                # Thread excess trim
                # ------------------
                if screw_form.threaded:
                    build_bottom_thread_excess_cutter_feature(doc, body, minor_cone, thread_profile_extents)
                    build_top_thread_excess_cutter_feature(doc, body, minor_cone, thread_profile_extents)

                # Lead-ins
                # --------
                if screw_form.bottom_led_in:
                    build_bottom_lead_in_cutter_feature(
                        doc,
                        body,
                        minor_cone,
                        screw_form.bottom_lead_in_radius_offset,
                        screw_form.bottom_lead_in_height,
                        thread_profile_extents
                    )
                if screw_form.top_led_in:
                    build_top_lead_in_cutter_feature(
                        doc,
                        body,
                        minor_cone,
                        screw_form.top_lead_in_radius_offset,
                        screw_form.top_lead_in_height,
                        thread_profile_extents
                    )

                child_bodies.append(body)

            parent_body = doc.addObject('PartDesign::Body', 'Final Screw')
            build_stack_feature(doc, parent_body, child_bodies)

            Gui.Selection.clearSelection()
            # Gui.Selection.addSelection(body.Document.Name, body.Name)
            doc.recompute()
            Gui.activeDocument().activeView().fitAll()

        def accept(self):
            doc.commitTransaction()
            Gui.Control.closeDialog()
            return True

        def reject(self):
            doc.abortTransaction()
            Gui.Control.closeDialog()
            return True

    Gui.Control.showDialog(ScrewCreateTaskPanel())