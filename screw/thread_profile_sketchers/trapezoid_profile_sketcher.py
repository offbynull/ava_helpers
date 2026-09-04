import math
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

import FreeCAD as App
import FreeCADGui as Gui
import Part
import Sketcher
from PySide import QtGui as QtWidgets

from logger import log, warn
from screw.file_utils import md5_hash
from screw.geometries.cone_frustum import ConeFrustum, Direction
from screw.geometries.cylinder import Cylinder
from screw.thread_profile_extents import ThreadProfileExtents
from screw.ui_components.collapsible_group_box import CollapsibleGroupBox

NAME = 'Trapezoid'

_0_MM = 0.0 * App.Units.MilliMetre
_0_DEG = 0.0 * App.Units.Degree
_90_DEG = 90.0 * App.Units.Degree


def _set_named_constraint(doc, sketch, name, value, recompute=False):
    log(f'{name=} {value=} {recompute=}')
    for i, c in enumerate(sketch.Constraints):
        if c.Name == name:
            sketch.setDatum(i, value)
            if recompute:
                doc.recompute([sketch])
            return
    raise ValueError(f'Constraint {name} not found')


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

        self.cone_slope_projection_group = CollapsibleGroupBox('Cone slope projection')
        self.cone_slope_projection_group.setCheckable(True)
        self.cone_slope_projection_group.setChecked(False)
        self.cone_slope_projection_group.toggled.connect(preview)
        cone_slope_projection_layout = QtWidgets.QFormLayout(self.cone_slope_projection_group)
        layout.addRow(self.cone_slope_projection_group)

        self.cone_slope_projection_angle = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.cone_slope_projection_angle.setProperty('value', -10 * App.Units.Degree)
        self.cone_slope_projection_angle.editingFinished.connect(preview)
        cone_slope_projection_layout.addRow('Cone slope projection angle:', self.cone_slope_projection_angle)

        self.round_tip_group = CollapsibleGroupBox('Rounded head')
        self.round_tip_group.setCheckable(True)
        self.round_tip_group.setChecked(False)
        self.round_tip_group.toggled.connect(preview)
        round_tip_layout = QtWidgets.QFormLayout(self.round_tip_group)
        layout.addRow(self.round_tip_group)

        self.blunt_head_distance = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.blunt_head_distance.setProperty('value', 0.001 * App.Units.MilliMetre)
        self.blunt_head_distance.editingFinished.connect(preview)
        round_tip_layout.addRow('Blunt head distance:', self.blunt_head_distance)

        self.blunt_head_angle = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.blunt_head_angle.setProperty('value', 0 * App.Units.Degree)
        self.blunt_head_angle.editingFinished.connect(preview)
        round_tip_layout.addRow('Blunt head angle:', self.blunt_head_angle)

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
        cone_slope_projection = None
        if self.cone_slope_projection_group.isChecked():
            cone_slope_projection = ConeSlopeProjection(
                angle=self.cone_slope_projection_angle.property('value'),
            )
        round_tip = None
        if self.round_tip_group.isChecked():
            round_tip = RoundTip(
                blunt_head_distance=self.blunt_head_distance.property('value'),
                blunt_head_angle=self.blunt_head_angle.property('value'),
            )
        return self.build_sketch_from_parameters(
            doc,
            body,
            minor_shape,
            thread_start_index,
            thread_starts,
            thread_axial_offset,
            thread_rotation_offset,
            thread_sink_offset,
            self.base.property('value'),
            self.height.property('value'),
            self.head_facing_angle.property('value'),
            self.lead_facing_angle.property('value'),
            cone_slope_projection,
            round_tip,
        )

    @staticmethod
    def build_sketch_from_parameters(
            doc: App.Document,
            body: App.DocumentObject,
            minor_shape: ConeFrustum | Cylinder,
            thread_start_index: int,
            thread_starts: int,
            thread_axial_offset: App.Units.Quantity,
            thread_rotation_offset: App.Units.Quantity,
            thread_sink_offset: App.Units.Quantity,
            trapezoid_base: App.Units.Quantity,
            trapezoid_height: App.Units.Quantity,
            head_facing_angle: App.Units.Quantity,
            lead_facing_angle: App.Units.Quantity,
            cone_slope_projection: ConeSlopeProjection | None,
            round_tip: RoundTip | None,
    ):
        fcstd_path = Path(__file__).parent / 'trapezoid_profile_sketches.FCStd'
        fcstd_md5_actual = md5_hash(fcstd_path)
        fcstd_md5_expected = 'eecebc38bc94fb3fc60abef2eec01bd9'
        if md5_hash(fcstd_path) != fcstd_md5_expected:
            warn(f'Trapezoid sketch file is unexpected: {fcstd_md5_actual=} vs {fcstd_md5_expected=}')
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = Path(temp_dir) / fcstd_path.name
            shutil.copy2(fcstd_path, temp_file)

            src = App.openDocument(str(temp_file), hidden=True)
            src_up_sketch, src_down_sketch = [o for o in src.Objects if o.TypeId == "Sketcher::SketchObject"]
            if (isinstance(minor_shape, ConeFrustum) and minor_shape.direction == Direction.UP) or isinstance(minor_shape, Cylinder):
                sketch = doc.copyObject(src_up_sketch, False)
            elif isinstance(minor_shape, ConeFrustum) and minor_shape.direction == Direction.DOWN:
                sketch = doc.copyObject(src_down_sketch, False)
            else:
                raise ValueError('This should never happen')
            App.closeDocument(src.Name)
            App.setActiveDocument(doc.Name)

            _set_named_constraint(doc, sketch, 'trap_base_length', -trapezoid_base)
            _set_named_constraint(doc, sketch, 'trap_height_length', trapezoid_height)
            _set_named_constraint(doc, sketch, 'trap_axial_offset', minor_shape.bottom_radius)
            _set_named_constraint(doc, sketch, 'sink_len', thread_sink_offset)
            _set_named_constraint(doc, sketch, 'trap_top_right_angle', _90_DEG + head_facing_angle)
            _set_named_constraint(doc, sketch, 'trap_bottom_right_angle', _90_DEG + lead_facing_angle)
            if round_tip is None:
                sketch.toggleConstruction(0)
                sketch.toggleConstruction(9)
                sketch.toggleConstruction(10)
                sketch.toggleConstruction(11)
            else:
                _set_named_constraint(doc, sketch, 'head_len', round_tip.blunt_head_distance)
                _set_named_constraint(doc, sketch, 'head_angle', round_tip.blunt_head_angle)
            cone_slope_projection_angle = _90_DEG
            if cone_slope_projection is not None:
                cone_slope_projection_angle = _90_DEG - cone_slope_projection.angle
            if (isinstance(minor_shape, ConeFrustum) and minor_shape.direction == Direction.UP) or isinstance(minor_shape, Cylinder):
                _set_named_constraint(doc, sketch, 'cone_slope_bottom_angle', cone_slope_projection_angle)
            elif isinstance(minor_shape, ConeFrustum) and minor_shape.direction == Direction.DOWN:
                _set_named_constraint(doc, sketch, 'cone_slope_top_angle', cone_slope_projection_angle)
            else:
                raise ValueError('This should never happen')
            minor_shape_angle = minor_shape.angle
            if minor_shape_angle == _0_DEG:  # Is it a cylinder?
                minor_shape_angle = 0.01 * App.Units.Degree  # Sketch solver fails at 0, so make it almost 0
            _set_named_constraint(doc, sketch, 'cone_slope_angle', minor_shape_angle)
            doc.recompute([sketch])

            plane = body.newObject('Part::DatumPlane', f'Thread Profile {thread_start_index} Plane')
            # Each start should be spaced out evenly across 360 degrees. The +.01 is added to avoid the
            # first thread from starting n at the cone/cylinder's seam, which is known to result in broken
            # geometry.
            #
            # TODO: Warn if rotation offset is 0.
            # TODO: Warn if thread axial offset results in thread that's self-intersecting.
            plane.AttachmentOffset = App.Placement(
                App.Vector(
                    0.0,
                    thread_axial_offset.Value,
                    0.0
                ),
                App.Rotation(
                    0.0,
                    (thread_start_index / thread_starts * 360.0) + thread_rotation_offset.Value,
                    0.0
                )
            )
            plane.MapReversed = False
            plane.AttachmentSupport = [(body.Origin, '')]
            plane.MapMode = 'ObjectXZ'
            plane.Visibility = False
            body.addObject(sketch)
            sketch.AttachmentSupport = plane, []
            sketch.MapMode = 'FlatFace'
            sketch.Visibility = False
            # It's the same sketch being generated everytime, but on a different face. The extents should
            # always be the same (or close enough, there may be rounding error). As such, the extents don't
            # need to be overridden here, but it also doesn't really matter if it is.
            # TODO: Warn if thread radius offset is 0, because being tangent with the cone results in broken
            #       geometry.
            return sketch, ThreadProfileExtents(doc, sketch, minor_shape.bottom_radius)