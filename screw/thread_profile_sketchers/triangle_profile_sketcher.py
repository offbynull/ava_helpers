import math

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui as QtWidgets

from screw.geometries.cone_frustum import ConeFrustum
from screw.geometries.cylinder import Cylinder
from screw.thread_profile_sketchers import trapezoid_profile_sketcher

NAME = 'Triangle'

_0_MM = 0.0 * App.Units.MilliMetre
_0_DEG = 0.0 * App.Units.Degree
_90_DEG = 90.0 * App.Units.Degree
_180_DEG = 180.0 * App.Units.Degree


def _isosceles_base(height, base_angle):
    angle_rad = base_angle.getValueAs(App.Units.Radian).Value
    return height * (2.0 / math.tan(angle_rad))


class Card:
    def __init__(self, preview):
        self.form = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(self.form)

        self.height = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.height.setProperty('unit', 'in')
        self.height.setProperty('value', App.Units.Quantity(1.5, 'mm'))
        self.height.editingFinished.connect(preview)
        layout.addRow('Height:', self.height)

        self.interior_base_angle = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.interior_base_angle.setProperty('unit', 'degree')
        self.interior_base_angle.setProperty('value', 60 * App.Units.Degree)
        self.interior_base_angle.editingFinished.connect(preview)
        layout.addRow('Interior base angle:', self.interior_base_angle)

        self.root_to_axis_projection_angle = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.root_to_axis_projection_angle.setProperty('unit', 'degree')
        self.root_to_axis_projection_angle.setProperty('value', 90 * App.Units.Degree)
        self.root_to_axis_projection_angle.editingFinished.connect(preview)
        layout.addRow('Root-to-axis projection angle:', self.root_to_axis_projection_angle)

    def sketch(self, doc: App.Document, sketch: App.DocumentObject, minor_shape: ConeFrustum | Cylinder, sink_depth: App.Units.Quantity):
        height = self.height.property('value')
        flank_angle = self.interior_base_angle.property('value')
        flank_cone_projection_angle = self.root_to_axis_projection_angle.property('value')
        base = _isosceles_base(height, flank_angle)
        return trapezoid_profile_sketcher.Card.sketch_from_parameters(
            doc,
            sketch,
            minor_shape,
            base,
            height,
            -(_90_DEG - flank_angle),
            -(_90_DEG - flank_angle),
            trapezoid_profile_sketcher.ConeSlopeProjection(
                angle=(_90_DEG - flank_cone_projection_angle)
            ),
            None,
            sink_depth,
        )
