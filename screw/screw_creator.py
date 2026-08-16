import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui

from logger import warn
from screw._lead_in import head_lead_in_cutter, end_lead_in_cutter
from screw._trigonometry import cone_frustum_to_angle
from screw.thread_profiles import square_profile, triangle_profile, trapezoid_profile

THREAD_PROFILES = [
    triangle_profile,
    square_profile,
    trapezoid_profile
]


def _excess_thread_trimmer(
        doc: App.Document,
        body: App.DocumentObject,
        name: str,
        radius: App.Units.Quantity,
        thread_profile_height: App.Units.Quantity,
        thread_profile_width: App.Units.Quantity,
        z_offset: App.Units.Quantity
):
    cut_body = doc.addObject('PartDesign::Body', f'{name} Body')
    cut_cylinder = cut_body.newObject('PartDesign::AdditiveCylinder', f'{name} Cylinder')
    cut_cylinder.Radius = radius + thread_profile_width
    cut_cylinder.Height = thread_profile_height
    cut_cylinder.Angle = 360 * App.Units.Degree
    cut_cylinder.FirstAngle = 0 * App.Units.Degree
    cut_cylinder.SecondAngle = 0 * App.Units.Degree
    boolean_cut = body.newObject('PartDesign::Boolean', f'{name} Thread Excess Cut')
    boolean_cut.addObjects([cut_body, ])
    boolean_cut.setObjects([cut_body, ])
    boolean_cut.Type = 1
    cut_body.Placement = App.Placement(
        App.Vector(0, 0, z_offset),
        App.Rotation(App.Vector(0, 0, 1), 0)
    )
    return boolean_cut


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

            self.cone_height = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
            self.cone_height.setProperty('value', 50 * App.Units.MilliMetre)
            self.cone_height.editingFinished.connect(self.preview)
            surface_shape_layout.addRow('Height:', self.cone_height)

            self.cone_point_end_radius = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
            self.cone_point_end_radius.setProperty('value', 10 * App.Units.MilliMetre)
            self.cone_point_end_radius.editingFinished.connect(self.preview)
            surface_shape_layout.addRow('Point end radius:', self.cone_point_end_radius)

            self.cone_point_head_radius = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
            self.cone_point_head_radius.setProperty('value', 50 * App.Units.MilliMetre)
            self.cone_point_head_radius.editingFinished.connect(self.preview)
            surface_shape_layout.addRow('Point head radius:', self.cone_point_head_radius)

            # Thread
            # -------
            self.thread_group = QtGui.QGroupBox('Thread')
            self.thread_group.setCheckable(True)
            self.thread_group.setChecked(True)
            self.thread_group.toggled.connect(self.preview)
            thread_layout = QtGui.QFormLayout(self.thread_group)
            layout.addRow(self.thread_group)
            
            self.thread_profile_combo = QtGui.QComboBox()
            self.thread_profile_stack = QtGui.QStackedWidget()
            self.thread_profile_cards = []
            for thread_profile in THREAD_PROFILES:
                self.thread_profile_combo.addItem(thread_profile.NAME)
                card = thread_profile.Card(self.preview)
                self.thread_profile_cards.append(card)
                self.thread_profile_stack.addWidget(card.form)
            self.thread_profile_combo.currentIndexChanged.connect(self.thread_profile_stack.setCurrentIndex)
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

            # Lead-in
            # -------
            self.end_lead_in_group = QtGui.QGroupBox('End lead-in')
            self.end_lead_in_group.setCheckable(True)
            self.end_lead_in_group.setChecked(False)
            self.end_lead_in_group.toggled.connect(self.preview)
            end_lead_in_layout = QtGui.QFormLayout(self.end_lead_in_group)
            layout.addRow(self.end_lead_in_group)

            self.end_lead_in_height = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
            self.end_lead_in_height.setProperty('value', 3 * App.Units.MilliMetre)
            self.end_lead_in_height.editingFinished.connect(self.preview)
            end_lead_in_layout.addRow('Height:', self.end_lead_in_height)

            self.end_lead_in_radius = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
            self.end_lead_in_radius.setProperty('value', 9 * App.Units.MilliMetre)
            self.end_lead_in_radius.editingFinished.connect(self.preview)
            end_lead_in_layout.addRow('Radius:', self.end_lead_in_radius)

            # Runout
            # ------
            self.head_lead_in_group = QtGui.QGroupBox('Head lead-in')
            self.head_lead_in_group.setCheckable(True)
            self.head_lead_in_group.setChecked(False)
            self.head_lead_in_group.toggled.connect(self.preview)
            head_lead_in_layout = QtGui.QFormLayout(self.head_lead_in_group)
            layout.addRow(self.head_lead_in_group)

            self.head_lead_in_height = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
            self.head_lead_in_height.setProperty('value', 3 * App.Units.MilliMetre)
            self.head_lead_in_height.editingFinished.connect(self.preview)
            head_lead_in_layout.addRow('Height:', self.head_lead_in_height)

            self.head_lead_in_radius = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
            self.head_lead_in_radius.setProperty('value', 9 * App.Units.MilliMetre)
            self.head_lead_in_radius.editingFinished.connect(self.preview)
            head_lead_in_layout.addRow('Radius:', self.head_lead_in_radius)

            doc.openTransaction('Create screw')
            self.preview()  # Initial launch

        def preview(self, *args):
            doc.abortTransaction()
            doc.openTransaction('Create screw')

            name = self.name.text()
            body = doc.addObject('PartDesign::Body', name)

            # Surface parameters
            # ------------------
            surface_point_end_radius = self.cone_point_end_radius.property('value')
            surface_point_head_radius = self.cone_point_head_radius.property('value')
            surface_height = self.cone_height.property('value')
            surface_cone_angle = cone_frustum_to_angle(surface_point_end_radius, surface_point_head_radius, surface_height)

            # Thread
            # ------
            thread_profile_heights = []
            thread_profile_widths = []
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
                    thread_profile_height, thread_profile_width = thread_profile.sketch(doc, sketch, surface_point_end_radius, surface_cone_angle)
                    thread_profile_widths.append(thread_profile_width)
                    thread_profile_heights.append(thread_profile_height)

                    helix = body.newObject('PartDesign::AdditiveHelix', f'Thread Helix {i}')
                    helix.Profile = (sketch, ['', ])
                    helix.ReferenceAxis = (sketch, ['V_Axis'])
                    helix.Mode = 0
                    helix.Pitch = self.thread_lead.property('value') + (0.0001 * App.Units.MilliMetre)  # You need this 0.0001mm or else the geometry breaks
                    helix.Height = surface_height + thread_profile_height
                    helix.Angle = surface_cone_angle
                    helix.Growth = 0
                    helix.LeftHanded = self.thread_left_handed.isChecked()
                    helix.Reversed = 0


            # Surface generation
            # ------------------
            surface = body.newObject('PartDesign::AdditiveCone', 'Surface Cone')
            surface.Radius1 = surface_point_end_radius
            surface.Radius2 = surface_point_head_radius
            surface.Height = surface_height
            surface.Angle = 360 * App.Units.Degree

            # Thread excess trim
            # ------------------
            max_thread_profile_height = max(thread_profile_heights, default=0 * App.Units.MilliMetre)
            max_thread_profile_width = max(thread_profile_widths, default=0 * App.Units.MilliMetre)
            _excess_thread_trimmer(
                doc,
                body,
                'Lower',
                surface_point_end_radius,
                max_thread_profile_height,
                # THIS IS BROKEN - IT SHOULD BE A CONE BEING EXTENDED IF THE SURFACE SHAPE IS A CONE
                10000 * App.Units.MilliMetre,  # thread_profile_width cuts too tight and leaves some pieces of the helix remaining in some cases
                -max_thread_profile_height
            )
            _excess_thread_trimmer(
                doc,
                body,
                'Upper',
                surface_point_head_radius,
                max_thread_profile_height,
                # THIS IS BROKEN - IT SHOULD BE A CONE BEING EXTENDED IF THE SURFACE SHAPE IS A CONE
                10000 * App.Units.MilliMetre,  # thread_profile_width, -- This cuts too tight and leaves some pieces of the helix remaining in some cases
                surface_height
            )

            # Lead ins
            # --------
            if self.end_lead_in_group.isChecked():
                end_lead_in_cutter(
                    doc,
                    body,
                    'End Lead-in',
                    surface_point_end_radius + thread_profile_width,
                    surface_point_head_radius + thread_profile_width,
                    surface_height,
                    self.end_lead_in_height.property('value'),
                    self.end_lead_in_radius.property('value')
                )
            if self.head_lead_in_group.isChecked():
                head_lead_in_cutter(
                    doc,
                    body,
                    'Head Lead-in',
                    surface_point_end_radius + thread_profile_width,
                    surface_point_head_radius + thread_profile_width,
                    surface_height,
                    self.head_lead_in_height.property('value'),
                    self.head_lead_in_radius.property('value')
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