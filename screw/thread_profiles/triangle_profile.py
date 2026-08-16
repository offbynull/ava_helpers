import FreeCAD as App
import FreeCADGui as Gui
import Part
import Sketcher
from PySide import QtGui as QtWidgets


NAME = 'Triangle'

class Card:
    def __init__(self, preview):
        self.form = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(self.form)

        self.height = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.height.setProperty('unit', 'in')
        self.height.setProperty('value', App.Units.Quantity(2, 'mm'))
        self.height.editingFinished.connect(preview)
        layout.addRow('Height:', self.height)

        self.angle = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.angle.setProperty('unit', 'degree')
        self.angle.setProperty('value', 60 * App.Units.Degree)
        self.angle.editingFinished.connect(preview)
        layout.addRow('Angle:', self.angle)

    def sketch(self, doc: App.Document, sketch: App.DocumentObject, radius: App.Units.Quantity, cone_angle: App.Units.Quantity):
        height = self.height.property('value')
        top_left = [-height, -height, 0]
        bottom_left = [-height, height, 0]
        middle_right = [height, App.Units.Quantity('0 mm'), 0]
        points = [top_left, bottom_left, middle_right]
        for p in points:
            p[0] += radius + height
            p[1] -= height
        lines = [
            Part.LineSegment(App.Vector(*top_left), App.Vector(*middle_right)),
            Part.LineSegment(App.Vector(*middle_right), App.Vector(*bottom_left)),
            Part.LineSegment(App.Vector(*bottom_left), App.Vector(*top_left)),
        ]
        height = height - (0.001  * App.Units.MilliMetre) # shrink slightly to avoid problems with helix fusing on pitch that makes the helix touch (e.g., thread profile with 2mm rise and a 2mm pitch)
        slope = (90 * App.Units.Degree) - cone_angle
        sketch.addGeometry(lines, False)
        sketch.addConstraint(Sketcher.Constraint('Coincident', 0, 1, 2, 2))
        sketch.addConstraint(Sketcher.Constraint('Coincident', 1, 2, 2, 1))
        sketch.addConstraint(Sketcher.Constraint('Coincident', 0, 2, 1, 1))
        sketch.addConstraint(Sketcher.Constraint('Angle', 1, 1, 0, 2, 60 * App.Units.Degree))
        sketch.addConstraint(Sketcher.Constraint('DistanceY', 0, 1, 1, 2, height))
        sketch.addConstraint(Sketcher.Constraint('PointOnObject', 1, 2, -1))
        sketch.addConstraint(Sketcher.Constraint('Angle', -1, 2, 2, 1, slope))
        sketch.addConstraint(Sketcher.Constraint('DistanceY', 0, 2, -height / 2))
        sketch.addConstraint(Sketcher.Constraint('DistanceX', 1, 2, radius))

        doc.recompute([sketch])  # Need to recompute sketch to apply constraints and stuff - required for pulling width
        middle_right_final = sketch.Geometry[0].EndPoint  # Endpoint of first line should be middle_right after constraints applied
        width = (middle_right_final.x * App.Units.MilliMetre) - radius

        return height, width