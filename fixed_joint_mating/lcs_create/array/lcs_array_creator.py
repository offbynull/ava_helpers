# https://chatgpt.com/share/6a42b763-d3c4-83ea-a8ab-978288c3d377
import math
import random
import string

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui

from fixed_joint_mating.lcs_utils import lcs_creator
from fixed_joint_mating.lcs_create.array._array_parameter_storage import write_inputs_to_varset
from fixed_joint_mating.lcs_create.array._utils import _attach_mater_and_orient, \
    _vector_pair_to_points_direction_length
from fixed_joint_mating.lcs_utils.lcs_identifier import MATER_LCS_IDENTIFIER
from fixed_joint_mating.lcs_create.array import mater_lcs_array_create_helpers
from fixed_joint_mating.lcs_create.array import _selection
from fixed_joint_mating.lcs_create.array._array_parameters import Offset
from fixed_joint_mating.lcs_create.array._array_parameters import OffsetApplicationCoordinateSystem
from logger import error, log, warn


def _create(
        doc: App.Document,
        selection: _selection.Selection,
        name_prefix: str,
        spacing: float,
        offset: Offset,
        store_varset: bool
) -> None:
    src = selection.source
    src_vertex_obj, src_vertex_name = selection.source_vertex
    _, src_face_name = selection.source_face
    _, src_edge_name = selection.source_edge if selection.source_edge else (None, None)
    dst = selection.destination
    dst_vertex_obj, _ = selection.destination_vertex

    if store_varset:
        write_inputs_to_varset(doc, f'{name_prefix}_{src.Label}_{MATER_LCS_IDENTIFIER}', selection, spacing, offset)

    ret = _vector_pair_to_points_direction_length(src_vertex_obj, dst_vertex_obj)
    if ret is None:
        error('Unable to extract point and direction.')
        return
    p0, p1, direction, length = ret

    if spacing == 0:
        error('Spacing cannot be zero.')
        return
    if spacing < 0:
        error('Spacing cannot be negative.')
        return

    count = int(math.floor(length / spacing)) + 1

    for mater_lcs_instance in range(count):
        mater_lcs = lcs_creator.run(
            doc=doc,
            name=f'{name_prefix}_{MATER_LCS_IDENTIFIER}_{mater_lcs_instance:03d}'
        )
        _attach_mater_and_orient(
            doc,
            p0,
            direction,
            mater_lcs,
            mater_lcs_instance,
            offset,
            spacing,
            src,
            src_edge_name,
            src_face_name,
            src_vertex_name
        )

    doc.recompute()
    log(f'Created {count} maters.')


def run(doc: App.Document | None = None):
    if doc is None:
        warn('AvaHelpersWorkbench: no active document.')
        return

    selection = _selection.extract_selection_inputs(doc)
    if selection is None:
        return

    class ArrayTaskPanel:
        def __init__(self):
            self.doc = App.ActiveDocument

            self.form = QtGui.QWidget()
            layout = QtGui.QFormLayout(self.form)

            self.name_prefix = QtGui.QLineEdit()
            self.name_prefix.setText(''.join(random.choices(string.ascii_letters + string.digits, k=6)))
            self.name_prefix.setPlaceholderText('Enter name prefix')
            # self.name_prefix.textChanged.connect(self.preview)
            self.name_prefix.editingFinished.connect(self.preview)
            layout.addRow('Name prefix:', self.name_prefix)

            self.space_between = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
            self.space_between.setProperty('unit', 'mm')
            self.space_between.setProperty('value', App.Units.Quantity(99999999, 'mm'))
            # self.space_between.valueChanged.connect(self.preview)
            self.space_between.editingFinished.connect(self.preview)
            layout.addRow('Space between:', self.space_between)

            layout.addRow(QtGui.QLabel(''))  # blank row as a spacer

            self.x_offset = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
            self.y_offset = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
            self.z_offset = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
            for w in (self.x_offset, self.y_offset, self.z_offset):
                w.setProperty('unit', 'mm')
                w.setProperty('value', App.Units.Quantity(0, 'mm'))
                # w.valueChanged.connect(self.preview)
                w.editingFinished.connect(self.preview)
            self.global_space_offset = QtGui.QCheckBox('Global')
            self.global_space_offset.setChecked(False)
            self.global_space_offset.stateChanged.connect(self.preview)
            layout.addRow('X offset:', self.x_offset)
            layout.addRow('Y offset:', self.y_offset)
            layout.addRow('Z offset:', self.z_offset)
            layout.addRow('Global:', self.global_space_offset)

            layout.addRow(QtGui.QLabel(''))  # blank row as a spacer

            self.store_varset = QtGui.QCheckBox('Store varset')
            self.store_varset.setChecked(False)
            self.store_varset.stateChanged.connect(self.preview)

            self.doc.openTransaction('Create mater LCS array')
            self.preview()  # Initial launch

        def preview(self, *args):
            self.doc.abortTransaction()
            self.doc.openTransaction('Create mater LCS array')

            name_prefix = self.name_prefix.text()
            length = self.space_between.property('value')
            offset = Offset(
                x=self.x_offset.property('value').getValueAs('mm').Value,
                y=self.y_offset.property('value').getValueAs('mm').Value,
                z=self.z_offset.property('value').getValueAs('mm').Value,
                coordinate_system_application=OffsetApplicationCoordinateSystem.GLOBAL if self.global_space_offset.isChecked() else OffsetApplicationCoordinateSystem.LCS,
            )
            store_varset = self.store_varset.isChecked()
            _create(doc, selection, name_prefix, length, offset, store_varset)

            self.doc.recompute()

        def accept(self):
            self.doc.commitTransaction()
            Gui.Control.closeDialog()
            return True

        def reject(self):
            self.doc.abortTransaction()
            Gui.Control.closeDialog()
            return True

    Gui.Control.showDialog(ArrayTaskPanel())
