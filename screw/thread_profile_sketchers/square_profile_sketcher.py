import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui as QtWidgets

from screw.geometries.cone_frustum import ConeFrustum
from screw.geometries.cylinder import Cylinder
from screw.thread_profile_sketchers import trapezoid_profile_sketcher

NAME = 'Square'

_0_MM = 0.0 * App.Units.MilliMetre
_0_DEG = 0.0 * App.Units.Degree
_90_DEG = 90.0 * App.Units.Degree
_180_DEG = 180.0 * App.Units.Degree

class Card:
    def __init__(self, preview):
        self.form = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(self.form)

        self.length = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.length.setProperty('value', App.Units.Quantity(2, 'mm'))
        self.length.editingFinished.connect(preview)
        layout.addRow('Length:', self.length)

        self.root_to_axis_projection_angle = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.root_to_axis_projection_angle.setProperty('unit', 'degree')
        self.root_to_axis_projection_angle.setProperty('value', 90 * App.Units.Degree)
        self.root_to_axis_projection_angle.editingFinished.connect(preview)
        layout.addRow('Root-to-axis projection angle:', self.root_to_axis_projection_angle)

    def build_sketch(
            self,
            doc: App.Document,
            body: App.DocumentObject,
            minor_shape: ConeFrustum | Cylinder,
            thread_start_index: int,
            thread_starts: int,
            thread_axial_offset: App.Units.Quantity,
            thread_rotation_offset: App.Units.Quantity,
            thread_sink_offset: App.Units.Quantity
    ):
        length = self.length.property('value')
        flank_cone_projection_angle = self.root_to_axis_projection_angle.property('value')
        return trapezoid_profile_sketcher.Card.build_sketch_from_parameters(
            doc,
            body,
            minor_shape,
            thread_start_index,
            thread_starts,
            thread_axial_offset,
            thread_rotation_offset,
            thread_sink_offset,
            length,
            length,
            _0_DEG,
            _0_DEG,
            trapezoid_profile_sketcher.ConeSlopeProjection(
                angle=(_90_DEG - flank_cone_projection_angle)
            ),
            None
        )

