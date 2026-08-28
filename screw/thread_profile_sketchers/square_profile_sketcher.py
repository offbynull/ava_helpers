import FreeCAD as App
import FreeCADGui as Gui
import Part
import Sketcher
from PySide import QtGui as QtWidgets

from screw.geometries.cone_frustum import ConeFrustum
from screw.geometries.cylinder import Cylinder
from screw.thread_profile_extents import ThreadProfileExtents

NAME = 'Square'

class Card:
    def __init__(self, preview):
        self.form = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(self.form)

        self.length = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.length.setProperty('value', App.Units.Quantity(2, 'mm'))
        self.length.editingFinished.connect(preview)

        layout.addRow('Length:', self.length)

    def sketch(self, doc: App.Document, sketch: App.DocumentObject, minor_cone: ConeFrustum | Cylinder):
        s = self.length.property('value') / 2
        top_left = [-s, -s, 0]
        top_right = [s, -s, 0]
        bottom_left = [-s, s, 0]
        bottom_right = [s, s, 0]
        points = [top_left, top_right, bottom_left, bottom_right]
        for p in points:
            p[0] += minor_cone.bottom_radius + s
            p[1] -= s
        lines = [
            Part.LineSegment(App.Vector(*top_left), App.Vector(*top_right)),
            Part.LineSegment(App.Vector(*top_right), App.Vector(*bottom_right)),
            Part.LineSegment(App.Vector(*bottom_right), App.Vector(*bottom_left)),
            Part.LineSegment(App.Vector(*bottom_left), App.Vector(*top_left)),
        ]
        slope = (90 * App.Units.Degree) + minor_cone.angle
        sketch.addGeometry(lines, False)
        sketch.addConstraint(Sketcher.Constraint('Horizontal', 0))
        sketch.addConstraint(Sketcher.Constraint('Horizontal', 2))
        sketch.addConstraint(Sketcher.Constraint('Vertical', 1))
        sketch.addConstraint(Sketcher.Constraint('Angle', 3, 1, 2, 2, slope))
        sketch.addConstraint(Sketcher.Constraint('Coincident', 0, 2, 1, 1))
        sketch.addConstraint(Sketcher.Constraint('Coincident', 1, 2, 2, 1))
        sketch.addConstraint(Sketcher.Constraint('Coincident', 2, 2, 3, 1))
        sketch.addConstraint(Sketcher.Constraint('Coincident', 3, 2, 0, 1))
        sketch.addConstraint(Sketcher.Constraint('DistanceX', 2, 2, 1, 2, s * 2 - (0.001  * App.Units.MilliMetre)))  # shrink slightly to avoid problems with helix fusing on pitch that makes the helix touch (e.g., thread profile with 2mm rise and a 2mm pitch)
        sketch.addConstraint(Sketcher.Constraint('DistanceY', 3, 2, 3, 1, s * 2 - (0.001 * App.Units.MilliMetre)))  # shrink slightly to avoid problems with helix fusing on pitch that makes the helix touch (e.g., thread profile with 2mm rise and a 2mm pitch)
        sketch.addConstraint(Sketcher.Constraint('DistanceX', 2, 2, minor_cone.bottom_radius))
        sketch.addConstraint(Sketcher.Constraint('DistanceY', 2, 2, 0))

        doc.recompute([sketch])
        shape = sketch.Shape.copy()
        inverted_placement_matrix = sketch.Placement.inverse().toMatrix()
        shape.transformShape(inverted_placement_matrix, True)
        return ThreadProfileExtents(shape.BoundBox, minor_cone.bottom_radius)
