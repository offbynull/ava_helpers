import math
from dataclasses import dataclass

import FreeCAD as App
import FreeCADGui as Gui
import Part
import Sketcher
from PySide import QtGui as QtWidgets

from screw.geometries.cone_frustum import ConeFrustum, Direction
from screw.geometries.cylinder import Cylinder
from screw.thread_profile_extents import ThreadProfileExtents


NAME = 'Trapezoid'

_0_MM = 0.0 * App.Units.MilliMetre
_0_DEG = 0.0 * App.Units.Degree
_90_DEG = 90.0 * App.Units.Degree


@dataclass
class ConeSlopeProjection:
    angle: App.Units.Quantity


@dataclass
class RoundTip:
    blunt_head_distance: App.Units.Quantity
    blunt_head_angle: App.Units.Quantity


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

        self.cone_slope_projection_override = QtWidgets.QGroupBox('Cone slope projection override')
        self.cone_slope_projection_override.setCheckable(True)
        self.cone_slope_projection_override.setChecked(False)
        self.cone_slope_projection_override.toggled.connect(preview)
        cone_slope_projection_layout = QtWidgets.QFormLayout(self.cone_slope_projection_override)
        layout.addRow(self.cone_slope_projection_override)

        self.cone_slope_projection_angle = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.cone_slope_projection_angle.setProperty('value', -10 * App.Units.Degree)
        self.cone_slope_projection_angle.editingFinished.connect(preview)
        cone_slope_projection_layout.addRow('Cone slope projection angle:', self.cone_slope_projection_angle)

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

    def sketch(self, doc: App.Document, sketch: App.DocumentObject, minor_shape: ConeFrustum | Cylinder, sink_depth: App.Units.Quantity):
        cone_slope_projection = None
        if self.cone_slope_projection_override.isChecked():
            cone_slope_projection = ConeSlopeProjection(
                angle=self.cone_slope_projection_angle.property('value'),
            )

        round_tip = None
        if self.round_tip_group.isChecked():
            round_tip = RoundTip(
                blunt_head_distance=self.blunt_head_distance.property('value'),
                blunt_head_angle=self.blunt_head_angle.property('value'),
            )

        return self.sketch_from_parameters(
            doc,
            sketch,
            minor_shape,
            self.base.property('value'),
            self.height.property('value'),
            self.head_facing_angle.property('value'),
            self.lead_facing_angle.property('value'),
            cone_slope_projection,
            round_tip,
            sink_depth,
        )

    @staticmethod
    def sketch_from_parameters(
        doc: App.Document,
        sketch: App.DocumentObject,
        minor_shape: ConeFrustum | Cylinder,
        trapezoid_base: App.Units.Quantity,
        trapezoid_height: App.Units.Quantity,
        head_facing_angle: App.Units.Quantity,
        lead_facing_angle: App.Units.Quantity,
        cone_slope_projection: ConeSlopeProjection | None,
        round_tip: RoundTip | None,
        sink_depth: App.Units.Quantity,
    ):
        raw_trapezoid_base = trapezoid_base.Value
        raw_trapezoid_height = trapezoid_height.Value

        r = minor_shape.bottom_radius.Value
        trap_bottom_left_vec = App.Vector(r, 0.0, 0.0)
        trap_top_left_vec = App.Vector(r, raw_trapezoid_base, 0.0)
        trap_bottom_right_vec = App.Vector(r + raw_trapezoid_height, 0.0, 0.0)
        trap_top_right_vec = App.Vector(r + raw_trapezoid_height, raw_trapezoid_base, 0.0)
        sink_top_right_vec = App.Vector(r + raw_trapezoid_height, 0.0, 0.0)
        sink_top_left_vec = App.Vector(r + raw_trapezoid_height - sink_depth.Value, 0.0, 0.0)
        sink_bottom_right_vec = App.Vector(
            r + raw_trapezoid_height,
            -raw_trapezoid_base,
            0.0,
        )
        sink_bottom_left_vec = App.Vector(
            r + raw_trapezoid_height - sink_depth.Value,
            -raw_trapezoid_base,
            0.0,
        )

        trap_right_id, trap_top_id, cone_slope_id, trap_bottom_id, trap_left_id, proj_bottom_id, proj_top_id, sink_top_id, sink_bottom_id, sink_left_id, sink_right_id = sketch.addGeometry(
            [
                Part.LineSegment(trap_bottom_right_vec, trap_top_right_vec),
                Part.LineSegment(trap_top_right_vec, trap_top_left_vec),
                Part.LineSegment(trap_top_left_vec, sink_bottom_right_vec),
                Part.LineSegment(trap_bottom_left_vec, trap_bottom_right_vec),
                Part.LineSegment(trap_bottom_left_vec, trap_top_left_vec),
                Part.LineSegment(sink_bottom_right_vec, trap_bottom_left_vec),
                Part.LineSegment(sink_top_right_vec, trap_top_left_vec),
                Part.LineSegment(sink_top_right_vec, sink_top_left_vec),
                Part.LineSegment(sink_bottom_left_vec, sink_bottom_right_vec),
                Part.LineSegment(sink_top_left_vec, sink_bottom_left_vec),
                Part.LineSegment(sink_top_right_vec, sink_bottom_right_vec),
            ]
        )

        head_taper_angle = (90 * App.Units.Degree) + head_facing_angle
        lead_taper_angle = (90 * App.Units.Degree) + lead_facing_angle
        cone_slope = minor_shape.angle
        if cone_slope_projection is not None:
            cone_slope_projection_angle = (90 * App.Units.Degree) - cone_slope_projection.angle
        else:
            cone_slope_projection_angle = (180 * App.Units.Degree) - lead_taper_angle

        sketch.addConstraint(Sketcher.Constraint('Coincident', trap_top_id, 1, trap_right_id, 2))
        sketch.addConstraint(Sketcher.Constraint('Coincident', trap_top_id, 2, trap_left_id, 2))
        sketch.addConstraint(Sketcher.Constraint('Coincident', trap_bottom_id, 2, trap_right_id, 1))
        sketch.addConstraint(Sketcher.Constraint('Coincident', trap_bottom_id, 1, trap_left_id, 1))
        sketch.addConstraint(Sketcher.Constraint('Vertical', trap_left_id))
        sketch.addConstraint(Sketcher.Constraint('Vertical', trap_right_id))
        sketch.addConstraint(Sketcher.Constraint('DistanceY', trap_left_id, 2, trap_left_id, 1, -raw_trapezoid_base))
        if isinstance(minor_shape, Cylinder):
            sketch.addConstraint(Sketcher.Constraint('DistanceX', trap_left_id, 1, minor_shape.bottom_radius.Value))
            sketch.addConstraint(Sketcher.Constraint('PointOnObject', trap_top_id, 2, -1))
        elif isinstance(minor_shape, ConeFrustum):
            if minor_shape.direction == Direction.UP:
                sketch.addConstraint(Sketcher.Constraint('DistanceX', trap_left_id, 1, minor_shape.bottom_radius.Value))
                sketch.addConstraint(Sketcher.Constraint('PointOnObject', trap_top_id, 2, -1))
            elif minor_shape.direction == Direction.DOWN:
                sketch.addConstraint(Sketcher.Constraint('DistanceX', proj_top_id, 1, minor_shape.bottom_radius.Value))
                sketch.addConstraint(Sketcher.Constraint('PointOnObject', sink_right_id, 1, -1))
            else:
                raise ValueError('This should never happen')
        else:
            raise ValueError('This should never happen')
        sketch.addConstraint(Sketcher.Constraint('DistanceX', trap_top_id, 2, trap_top_id, 1, raw_trapezoid_height))
        sketch.addConstraint(Sketcher.Constraint('Angle', trap_left_id, 2, trap_top_id, 2, head_taper_angle))
        sketch.addConstraint(Sketcher.Constraint('Angle', trap_bottom_id, 1, trap_left_id, 1, lead_taper_angle))
        sketch.toggleConstruction(trap_left_id)

        sketch.addConstraint(Sketcher.Constraint('Horizontal', sink_top_id))
        sketch.addConstraint(Sketcher.Constraint('Horizontal', sink_bottom_id))
        sketch.addConstraint(Sketcher.Constraint('Vertical', sink_left_id))
        sketch.addConstraint(Sketcher.Constraint('Vertical', sink_right_id))
        sketch.addConstraint(Sketcher.Constraint('DistanceX', sink_bottom_id, 1, sink_bottom_id, 2, sink_depth))
        sketch.addConstraint(Sketcher.Constraint('Coincident', sink_left_id, 2, sink_bottom_id, 1))
        sketch.addConstraint(Sketcher.Constraint('Coincident', sink_left_id, 1, sink_top_id, 2))
        sketch.addConstraint(Sketcher.Constraint('Coincident', sink_right_id, 2, sink_bottom_id, 2))
        sketch.addConstraint(Sketcher.Constraint('Coincident', sink_right_id, 1, sink_top_id, 1))
        sketch.toggleConstruction(sink_right_id)

        sketch.addConstraint(Sketcher.Constraint('Coincident', proj_top_id, 2, trap_top_id, 2))
        sketch.addConstraint(Sketcher.Constraint('Coincident', proj_top_id, 1, sink_right_id, 1))
        sketch.addConstraint(Sketcher.Constraint('Coincident', proj_bottom_id, 2, trap_bottom_id, 1))
        sketch.addConstraint(Sketcher.Constraint('Coincident', proj_bottom_id, 1, sink_right_id, 2))

        if isinstance(minor_shape, Cylinder):
            sketch.toggleConstruction(cone_slope_id)
            sketch.addConstraint(Sketcher.Constraint('Coincident', cone_slope_id, 1, trap_top_id, 2))
            sketch.addConstraint(Sketcher.Constraint('Coincident', cone_slope_id, 2, sink_bottom_id, 2))
            # sketch.addConstraint(Sketcher.Constraint('Angle', cone_slope_id, 1, trap_left_id, 2, cone_slope))
            # Do not use cone_slope_projection_angle - this is a cylinder, it doesn't project any farther than the trapezoid
            sketch.addConstraint(Sketcher.Constraint('Angle', trap_left_id, 1, proj_bottom_id, 2, _90_DEG))
            sketch.addConstraint(Sketcher.Constraint('Angle', proj_top_id, 2, trap_left_id, 2, _90_DEG))
            sketch.addConstraint(Sketcher.Constraint('DistanceX', 6, 1, 6, 2, _0_MM))
        elif isinstance(minor_shape, ConeFrustum):
            if minor_shape.direction == Direction.UP:
                sketch.toggleConstruction(cone_slope_id)
                sketch.addConstraint(Sketcher.Constraint('Coincident', cone_slope_id, 1, trap_top_id, 2))
                sketch.addConstraint(Sketcher.Constraint('Coincident', cone_slope_id, 2, sink_bottom_id, 2))
                sketch.addConstraint(Sketcher.Constraint('Angle', cone_slope_id, 1, trap_left_id, 2, cone_slope))
                sketch.addConstraint(Sketcher.Constraint('Angle', trap_left_id, 1, proj_bottom_id, 2, cone_slope_projection_angle))
                sketch.addConstraint(Sketcher.Constraint('Angle', proj_top_id, 2, trap_left_id, 2, _90_DEG))
            elif minor_shape.direction == Direction.DOWN:
                sketch.toggleConstruction(cone_slope_id)
                sketch.addConstraint(Sketcher.Constraint('Coincident', cone_slope_id, 1, trap_bottom_id, 1))
                sketch.addConstraint(Sketcher.Constraint('Coincident', cone_slope_id, 2, sink_top_id, 2))
                sketch.addConstraint(Sketcher.Constraint('Angle', cone_slope_id, 1, trap_left_id, 1, -cone_slope))
                sketch.addConstraint(Sketcher.Constraint('Angle', trap_left_id, 2, proj_top_id, 2, -cone_slope_projection_angle))
                sketch.addConstraint(Sketcher.Constraint('Angle', trap_left_id, 2, proj_bottom_id, 2, -_90_DEG))
            else:
                raise ValueError('This should never happen')
        else:
            raise ValueError('This should never happen')

        if round_tip is not None:
            doc.recompute([sketch])  # Need to recompute sketch to apply constraints and stuff - required for pulling coordinates
            top_right_geo = sketch.Geometry[trap_right_id]
            head_line_x_midpoint = top_right_geo.StartPoint.x + (top_right_geo.EndPoint.x - top_right_geo.StartPoint.x) / 2
            head_line_y_midpoint = top_right_geo.StartPoint.y + (top_right_geo.EndPoint.y - top_right_geo.StartPoint.y) / 2
            head_top_arc_id, head_bottom_arc_id, blunt_head_line_id = sketch.addGeometry([
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
            sketch.toggleConstruction(trap_right_id)
            sketch.addConstraint(Sketcher.Constraint('Coincident', head_top_arc_id, 2, trap_right_id, 2))
            sketch.addConstraint(Sketcher.Constraint('Coincident', head_bottom_arc_id, 1, trap_right_id, 1))
            sketch.addConstraint(Sketcher.Constraint('Tangent', trap_top_id, head_top_arc_id))
            sketch.addConstraint(Sketcher.Constraint('Tangent', trap_bottom_id, head_bottom_arc_id))
            sketch.addConstraint(Sketcher.Constraint('Coincident', blunt_head_line_id, 2, head_top_arc_id, 1))
            sketch.addConstraint(Sketcher.Constraint('Coincident', blunt_head_line_id, 1, head_bottom_arc_id, 2))
            sketch.delConstraintOnPoint(blunt_head_line_id, 1)  # Remove coincident constraints just added - they seed the position for the tangents below. Tangents keep it coincident.
            sketch.delConstraintOnPoint(blunt_head_line_id, 2)
            sketch.addConstraint(Sketcher.Constraint('Angle', trap_right_id, 2, blunt_head_line_id, 2, round_tip.blunt_head_angle))
            sketch.addConstraint(Sketcher.Constraint('Distance', blunt_head_line_id, round_tip.blunt_head_distance))
            sketch.addConstraint(Sketcher.Constraint('Tangent', blunt_head_line_id, 2, head_top_arc_id, 1))
            sketch.addConstraint(Sketcher.Constraint('Tangent', blunt_head_line_id, 1, head_bottom_arc_id, 2))

        return ThreadProfileExtents(doc, sketch, minor_shape.bottom_radius)
