import FreeCAD as App
import FreeCADGui as Gui
import Part
import Sketcher
from PySide import QtGui as QtWidgets

from screw.geometries.cone_frustum import ConeFrustum
from screw.geometries.cylinder import Cylinder
from screw.thread_profile_extents import ThreadProfileExtents

NAME = 'Triangle'

_180_DEG = 180 * App.Units.Degree


class Card:
    def __init__(self, preview):
        self.form = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(self.form)

        self.height = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.height.setProperty('unit', 'in')
        self.height.setProperty('value', App.Units.Quantity(1.5, 'mm'))
        self.height.editingFinished.connect(preview)
        layout.addRow('Height:', self.height)

        self.angle = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.angle.setProperty('unit', 'degree')
        self.angle.setProperty('value', 60 * App.Units.Degree)
        self.angle.editingFinished.connect(preview)
        layout.addRow('Angle:', self.angle)

    def sketch(self, doc: App.Document, sketch: App.DocumentObject, minor_cone: ConeFrustum | Cylinder):
        height = self.height.property('value')
        angle = self.angle.property('value')
        top_left = [-height, -height, 0]
        bottom_left = [-height, height, 0]
        middle_right = [height, App.Units.Quantity('0 mm'), 0]
        points = [top_left, bottom_left, middle_right]
        for p in points:
            p[0] += minor_cone.bottom_radius + height
            p[1] -= height
        lines = [
            Part.LineSegment(App.Vector(*top_left), App.Vector(*middle_right)),
            Part.LineSegment(App.Vector(*middle_right), App.Vector(*bottom_left)),
            Part.LineSegment(App.Vector(*bottom_left), App.Vector(*top_left)),
        ]
        # height = height - (0.001  * App.Units.MilliMetre) # shrink slightly to avoid problems with helix fusing on pitch that makes the helix touch (e.g., thread profile with 2mm rise and a 2mm pitch)
        slope = (90 * App.Units.Degree) - minor_cone.angle
        sketch.addGeometry(lines, False)
        sketch.addConstraint(Sketcher.Constraint('Coincident', 0, 1, 2, 2))
        sketch.addConstraint(Sketcher.Constraint('Coincident', 1, 2, 2, 1))
        sketch.addConstraint(Sketcher.Constraint('Coincident', 0, 2, 1, 1))
        sketch.addConstraint(Sketcher.Constraint('Angle', 1, 1, 0, 2, angle))
        sketch.addConstraint(Sketcher.Constraint('DistanceX', 1, 2, 0, 2, height))
        sketch.addConstraint(Sketcher.Constraint('Angle', 2, 1, 1, 2, ((_180_DEG - angle) / 2)))
        sketch.addConstraint(Sketcher.Constraint('PointOnObject', 1, 2, -1))
        sketch.addConstraint(Sketcher.Constraint('Vertical', 2))
        sketch.addConstraint(Sketcher.Constraint('DistanceX', 1, 2, minor_cone.bottom_radius))
        sketch.toggleConstruction(2)

        sketch.addGeometry(
            [
                Part.LineSegment(
                    App.Vector(minor_cone.bottom_radius.Value, 0.0, 0.0),
                    App.Vector(minor_cone.bottom_radius.Value, 1.0, 0.0)
                ),
                Part.LineSegment(
                    App.Vector(minor_cone.bottom_radius.Value, 0.0, 0.0),
                    App.Vector(minor_cone.bottom_radius.Value, 1.0, 0.0))
            ],
            False
        )
        sketch.addConstraint(Sketcher.Constraint('Coincident', 3, 1, 1, 2))
        sketch.addConstraint(Sketcher.Constraint('Angle', -1, 2, 3, 1, slope))
        sketch.addConstraint(Sketcher.Constraint('Coincident', 4, 2, 3, 2))
        sketch.addConstraint(Sketcher.Constraint('Coincident', 4, 1, 0, 1))
        sketch.addConstraint(Sketcher.Constraint('Parallel', 4, 0))

        return ThreadProfileExtents(doc, sketch, minor_cone.bottom_radius)
