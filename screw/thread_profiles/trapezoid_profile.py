import math

import FreeCAD as App
import FreeCADGui as Gui
import Part
import Sketcher
from PySide import QtGui as QtWidgets

from screw.cone_frustum_parameters import ConeFrustumParameters
from screw.thread_profile_extents import ThreadProfileExtents

NAME = 'Trapezoid'

class Card:
    def __init__(self, preview):
        self.form = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(self.form)

        self.base = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.base.setProperty('value', App.Units.Quantity(2, 'mm'))
        self.base.editingFinished.connect(preview)
        layout.addRow('Base:', self.base)

        self.height = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.height.setProperty('value', App.Units.Quantity(2, 'mm'))
        self.height.editingFinished.connect(preview)
        layout.addRow('Height:', self.height)

        self.head_facing_angle = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.head_facing_angle.setProperty('value', -10 * App.Units.Degree)
        self.head_facing_angle.editingFinished.connect(preview)
        layout.addRow('Head-facing angle:', self.head_facing_angle)

        self.lead_facing_angle = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.lead_facing_angle.setProperty('value', -10 * App.Units.Degree)
        self.lead_facing_angle.editingFinished.connect(preview)
        layout.addRow('Lead-facing angle:', self.lead_facing_angle)

        self.cone_slope_projection_angle = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.cone_slope_projection_angle.setProperty('value', -10 * App.Units.Degree)
        self.cone_slope_projection_angle.editingFinished.connect(preview)
        layout.addRow('Cone slope projection angle:', self.cone_slope_projection_angle)

        self.round_tip_group = QtWidgets.QGroupBox('Rounded head')
        self.round_tip_group.setCheckable(True)
        self.round_tip_group.setChecked(False)
        self.round_tip_group.toggled.connect(preview)
        round_tip_layout = QtWidgets.QFormLayout(self.round_tip_group)
        layout.addRow(self.round_tip_group)

        self.blunt_head_distance = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.blunt_head_distance.setProperty('value', App.Units.Quantity(0.001, 'mm'))
        self.blunt_head_distance.editingFinished.connect(preview)
        round_tip_layout.addRow('Blunt head distance:', self.blunt_head_distance)

        self.blunt_head_angle = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.blunt_head_angle.setProperty('value', 0 * App.Units.Degree)
        self.blunt_head_angle.editingFinished.connect(preview)
        round_tip_layout.addRow('Blunt head angle:', self.blunt_head_angle)

    def sketch(self, doc: App.Document, sketch: App.DocumentObject, minor_cone: ConeFrustumParameters):
        raw_trapezoid_base = self.base.property('value').Value
        raw_trapezoid_height = self.height.property('value').Value
        top_left = [0, 0, 0]
        top_right = [0, raw_trapezoid_height, 0]
        bottom_left = [-raw_trapezoid_base, 0, 0]
        bottom_right = [-raw_trapezoid_base, raw_trapezoid_height, 0]
        points = [top_left, top_right, bottom_left, bottom_right]
        for p in points:
            p[0] += minor_cone.bottom_radius.Value
        lines = [
            Part.LineSegment(App.Vector(*top_left), App.Vector(*top_right)),
            Part.LineSegment(App.Vector(*top_right), App.Vector(*bottom_right)),
            Part.LineSegment(App.Vector(*bottom_right), App.Vector(*bottom_left)),
            Part.LineSegment(App.Vector(*bottom_left), App.Vector(*top_left)),
            Part.LineSegment(App.Vector(*top_left), App.Vector(*bottom_right)),
            Part.LineSegment(App.Vector(*top_right), App.Vector(*bottom_left)),
        ]
        slope = minor_cone.angle
        sketch.addGeometry(lines, False)
        head_taper_angle = (90 * App.Units.Degree) + self.head_facing_angle.property('value')
        lead_taper_angle = (90 * App.Units.Degree) + self.lead_facing_angle.property('value')
        cone_slope_projection_angle = (90 * App.Units.Degree) - self.cone_slope_projection_angle.property('value')

        sketch.addConstraint(Sketcher.Constraint('Coincident', 0, 2, 1, 1))
        sketch.addConstraint(Sketcher.Constraint('Coincident', 1, 2, 2, 1))
        sketch.addConstraint(Sketcher.Constraint('Coincident', 2, 2, 3, 1))
        sketch.addConstraint(Sketcher.Constraint('Coincident', 3, 2, 0, 1))

        sketch.addConstraint(Sketcher.Constraint('PointOnObject', 4, 1, -1))
        sketch.addConstraint(Sketcher.Constraint('Vertical', 4))
        sketch.addConstraint(Sketcher.Constraint('DistanceY', 4, 2, -raw_trapezoid_base))
        sketch.addConstraint(Sketcher.Constraint('DistanceX', 4, 1, minor_cone.bottom_radius.Value))
        sketch.toggleConstruction(4)
        sketch.delConstraint(2)
        sketch.addConstraint(Sketcher.Constraint('Coincident', 3, 1, 4, 2))
        sketch.addConstraint(Sketcher.Constraint('Coincident', 1, 2, 4, 1))
        sketch.addConstraint(Sketcher.Constraint('Coincident', 5, 2, 3, 1))
        sketch.addConstraint(Sketcher.Constraint('Coincident', 5, 1, 2, 2))
        sketch.addConstraint(Sketcher.Constraint('DistanceX', 1, 2, 0, 2, raw_trapezoid_height))
        sketch.addConstraint(Sketcher.Constraint('Angle', 4, 2, 5, 2, cone_slope_projection_angle))

        sketch.addConstraint(Sketcher.Constraint('Angle', 2, 1, 4, 1, slope))
        sketch.addConstraint(Sketcher.Constraint('Angle', 4, 1, 1, 2, head_taper_angle))
        sketch.addConstraint(Sketcher.Constraint('Angle', 3, 1, 4, 2, lead_taper_angle))
        sketch.addConstraint(Sketcher.Constraint('Vertical', 0))

        if self.round_tip_group.isChecked():
            doc.recompute([sketch])  # Need to recompute sketch to apply constraints and stuff - required for pulling coordinates
            head_line_x_midpoint = sketch.Geometry[0].StartPoint.x + (sketch.Geometry[0].EndPoint.x - sketch.Geometry[0].StartPoint.x) / 2
            head_line_y_midpoint = sketch.Geometry[0].StartPoint.y + (sketch.Geometry[0].EndPoint.y - sketch.Geometry[0].StartPoint.y) / 2
            sketch.addGeometry([
                Part.ArcOfCircle(
                    Part.Circle(
                        App.Vector(head_line_x_midpoint, head_line_y_midpoint, 0.0),
                        App.Vector(0.0, 0.0, 1.0),
                        0.5
                    ),
                    math.radians(0),
                    math.radians(90)
                ),
                Part.ArcOfCircle(
                    Part.Circle(
                        App.Vector(head_line_x_midpoint, head_line_y_midpoint, 0.0),
                        App.Vector(0.0, 0.0, 1.0),
                        0.5
                    ),
                    math.radians(-90),
                    math.radians(0)
                ),
                Part.LineSegment(
                    App.Vector(head_line_x_midpoint, head_line_y_midpoint-0.0001, 0.0),
                    App.Vector(head_line_x_midpoint, head_line_y_midpoint+0.0001, 0.0)
                ),
            ])
            sketch.toggleConstruction(0)
            sketch.addConstraint(Sketcher.Constraint('Coincident',6,2,0,2))
            sketch.addConstraint(Sketcher.Constraint('Coincident',7,1,0,1))
            sketch.addConstraint(Sketcher.Constraint('Tangent',1,6))
            sketch.addConstraint(Sketcher.Constraint('Tangent',3,7))
            sketch.addConstraint(Sketcher.Constraint('Coincident',8,2,6,1))
            sketch.addConstraint(Sketcher.Constraint('Coincident',8,1,7,2))
            sketch.addConstraint(Sketcher.Constraint('Tangent', 8,1,7,2))
            sketch.delConstraintOnPoint(8, 1)
            sketch.addConstraint(Sketcher.Constraint('Tangent', 8,2,6,1))
            sketch.delConstraintOnPoint(8, 2)
            blunt_head_angle = self.blunt_head_angle.property('value')
            blunt_head_distance = self.blunt_head_distance.property('value')
            sketch.addConstraint(Sketcher.Constraint('Angle', 0, 2, 8, 2, blunt_head_angle))
            sketch.addConstraint(Sketcher.Constraint('Distance', 8, blunt_head_distance))

        doc.recompute([sketch])
        return ThreadProfileExtents(sketch.Shape.BoundBox, minor_cone.bottom_radius)
