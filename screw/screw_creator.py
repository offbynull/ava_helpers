import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui

from logger import warn
from screw._lead_in_cutter import cut_lead_in_upper, cut_lead_in_lower
from screw._thread_excess_cutter import cut_excess_thread_lower, cut_excess_thread_upper
from screw.cone_frustum_parameters import ConeFrustumParameters
from screw.thread_profile_extents_set import ThreadProfileExtentsSet
from screw.thread_profiles import square_profile, triangle_profile, trapezoid_profile
from screw.ui_components.tight_stacked_widgets import TightStackedWidget

THREAD_PROFILES = [
    triangle_profile,
    square_profile,
    trapezoid_profile
]


def run(doc: App.Document) -> None:
    if doc is None:
        warn('AvaHelpersWorkbench: no active document.')
        return

    class ScrewCreateTaskPanel:
        def __init__(self):
            self.form = QtGui.QWidget()

            self.form = QtGui.QWidget()
            layout = QtGui.QFormLayout(self.form)

            self.name = QtGui.QLineEdit()
            self.name.setText('Screw')
            self.name.setPlaceholderText('Enter name')
            self.name.editingFinished.connect(self.preview)
            layout.addRow('Name:', self.name)

            # Surface
            # -------
            self.surface_shape_group = QtGui.QGroupBox('Surface')
            self.surface_shape_group.toggled.connect(self.preview)
            surface_shape_layout = QtGui.QFormLayout(self.surface_shape_group)
            layout.addRow(self.surface_shape_group)

            self.cone_distance_between_radiuses = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
            self.cone_distance_between_radiuses.setProperty('value', 50 * App.Units.MilliMetre)
            self.cone_distance_between_radiuses.editingFinished.connect(self.preview)
            surface_shape_layout.addRow('Distance:', self.cone_distance_between_radiuses)

            self.cone_top_radius = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
            self.cone_top_radius.setProperty('value', 50 * App.Units.MilliMetre)
            self.cone_top_radius.editingFinished.connect(self.preview)
            surface_shape_layout.addRow('Top radius:', self.cone_top_radius)

            self.cone_bottom_radius = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
            self.cone_bottom_radius.setProperty('value', 10 * App.Units.MilliMetre)
            self.cone_bottom_radius.editingFinished.connect(self.preview)
            surface_shape_layout.addRow('Bottom radius:', self.cone_bottom_radius)

            # Thread
            # -------
            self.thread_group = QtGui.QGroupBox('Thread')
            self.thread_group.setCheckable(True)
            self.thread_group.setChecked(True)
            self.thread_group.toggled.connect(self.preview)
            thread_layout = QtGui.QFormLayout(self.thread_group)
            layout.addRow(self.thread_group)
            
            self.thread_profile_combo = QtGui.QComboBox()
            self.thread_profile_stack = TightStackedWidget()
            self.thread_profile_cards = []
            for thread_profile in THREAD_PROFILES:
                self.thread_profile_combo.addItem(thread_profile.NAME)
                card = thread_profile.Card(self.preview)
                self.thread_profile_cards.append(card)
                self.thread_profile_stack.addWidget(card.form)
            self.thread_profile_combo.currentIndexChanged.connect(self.thread_profile_stack.setCurrentIndex)
            self.thread_profile_combo.currentIndexChanged.connect(lambda _: self.thread_profile_stack.updateGeometry())
            self.thread_profile_combo.currentIndexChanged.connect(self.preview)
            thread_layout.addRow('Profile:', self.thread_profile_combo)
            thread_layout.addRow(self.thread_profile_stack)

            self.thread_starts = QtGui.QSpinBox()
            self.thread_starts.setMinimum(1)
            self.thread_starts.setValue(1)
            self.thread_starts.editingFinished.connect(self.preview)
            thread_layout.addRow('Starts:', self.thread_starts)

            self.thread_lead = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
            self.thread_lead.setProperty('value', 5 * App.Units.MilliMetre)
            self.thread_lead.editingFinished.connect(self.preview)
            thread_layout.addRow('Lead:', self.thread_lead)

            self.thread_left_handed = Gui.UiLoader().createWidget('QCheckBox')
            self.thread_left_handed.setChecked(False)
            self.thread_left_handed.toggled.connect(self.preview)
            thread_layout.addRow('Left-handed:', self.thread_left_handed)

            # Top lead-in
            # -----------
            self.top_lead_in_group = QtGui.QGroupBox('Top lead-in')
            self.top_lead_in_group.setCheckable(True)
            self.top_lead_in_group.setChecked(False)
            self.top_lead_in_group.toggled.connect(self.preview)
            top_lead_in_layout = QtGui.QFormLayout(self.top_lead_in_group)
            layout.addRow(self.top_lead_in_group)

            self.top_lead_in_height = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
            self.top_lead_in_height.setProperty('value', 3 * App.Units.MilliMetre)
            self.top_lead_in_height.editingFinished.connect(self.preview)
            top_lead_in_layout.addRow('Height:', self.top_lead_in_height)

            self.top_lead_in_radius = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
            self.top_lead_in_radius.setProperty('value', 9 * App.Units.MilliMetre)
            self.top_lead_in_radius.editingFinished.connect(self.preview)
            top_lead_in_layout.addRow('Radius:', self.top_lead_in_radius)
            
            # Bottom lead-in
            # --------------
            self.bottom_lead_in_group = QtGui.QGroupBox('Bottom lead-in')
            self.bottom_lead_in_group.setCheckable(True)
            self.bottom_lead_in_group.setChecked(False)
            self.bottom_lead_in_group.toggled.connect(self.preview)
            bottom_lead_in_layout = QtGui.QFormLayout(self.bottom_lead_in_group)
            layout.addRow(self.bottom_lead_in_group)

            self.bottom_lead_in_height = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
            self.bottom_lead_in_height.setProperty('value', 3 * App.Units.MilliMetre)
            self.bottom_lead_in_height.editingFinished.connect(self.preview)
            bottom_lead_in_layout.addRow('Height:', self.bottom_lead_in_height)

            self.bottom_lead_in_radius = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
            self.bottom_lead_in_radius.setProperty('value', 9 * App.Units.MilliMetre)
            self.bottom_lead_in_radius.editingFinished.connect(self.preview)
            bottom_lead_in_layout.addRow('Radius:', self.bottom_lead_in_radius)

            doc.openTransaction('Create screw')
            self.preview()  # Initial launch

        def preview(self, *args):
            doc.abortTransaction()
            doc.openTransaction('Create screw')

            name = self.name.text()
            body = doc.addObject('PartDesign::Body', name)

            # Surface parameters
            # ------------------
            minor_cone = ConeFrustumParameters(
                self.cone_bottom_radius.property('value'),
                self.cone_top_radius.property('value'),
                self.cone_distance_between_radiuses.property('value')
            )

            # Thread
            # ------
            thread_profile_extents_set = ThreadProfileExtentsSet()
            if self.thread_group.isChecked():
                for i in range(0, self.thread_starts.value()):
                    plane = body.newObject('Part::DatumPlane', f'Thread Profile {i} Plane')
                    plane.AttachmentOffset = App.Placement(
                        App.Vector(0.0, 0.0, 0.0),
                        App.Rotation(0.0, i / self.thread_starts.value() * 360.0, 0.0)
                    )
                    plane.MapReversed = False
                    plane.AttachmentSupport = [(body.Origin, '')]
                    plane.MapMode = 'ObjectXZ'
                    plane.Visibility = False
                    sketch = body.newObject('Sketcher::SketchObject', f'Thread Profile {i}')
                    sketch.AttachmentSupport = plane, []
                    sketch.MapMode = 'FlatFace'
                    sketch.Visibility = False
                    thread_profile = self.thread_profile_cards[self.thread_profile_combo.currentIndex()]
                    thread_profile_extents = thread_profile.sketch(doc, sketch, minor_cone)
                    thread_profile_extents_set.add(thread_profile_extents)

                    helix = body.newObject('PartDesign::AdditiveHelix', f'Thread Helix {i}')
                    helix.Profile = (sketch, ['', ])
                    helix.ReferenceAxis = (sketch, ['V_Axis'])
                    helix.Mode = 0
                    helix.Pitch = self.thread_lead.property('value') + (0.0001 * App.Units.MilliMetre)  # Need 0.0001mm or else the geometry breaks
                    helix.Height = minor_cone.distance_between_radiuses + thread_profile_extents.underneath_distance  # Height is the height of the frustum + continuing further up until the bottom of the sketch touches the tip of the frustum
                    helix.Angle = minor_cone.angle
                    helix.Growth = 0
                    helix.LeftHanded = self.thread_left_handed.isChecked()
                    helix.Reversed = 0

            # Surface generation
            # ------------------
            surface = body.newObject('PartDesign::AdditiveCone', 'Surface Cone')
            surface.Radius1 = minor_cone.bottom_radius
            surface.Radius2 = minor_cone.top_radius
            surface.Height = minor_cone.distance_between_radiuses
            surface.Angle = 360 * App.Units.Degree

            # Thread excess trim
            # ------------------
            cut_excess_thread_lower(
                body,
                minor_cone,
                thread_profile_extents_set.underneath_distance,
                thread_profile_extents_set.beside_distance
            )
            cut_excess_thread_upper(
                body,
                minor_cone,
                thread_profile_extents_set.underneath_distance + thread_profile_extents_set.ontop_distance,
                thread_profile_extents_set.beside_distance
            )

            # Lead-ins
            # --------
            if self.bottom_lead_in_group.isChecked():
                cut_lead_in_lower(
                    doc,
                    body,
                    minor_cone,
                    self.bottom_lead_in_radius.property('value'),
                    self.bottom_lead_in_height.property('value'),
                    thread_profile_extents_set.beside_distance
                )
            if self.top_lead_in_group.isChecked():
                cut_lead_in_upper(
                    doc,
                    body,
                    minor_cone,
                    self.top_lead_in_height.property('value'),
                    self.top_lead_in_radius.property('value'),
                    thread_profile_extents_set.beside_distance
                )

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