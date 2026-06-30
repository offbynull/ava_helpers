import string
import random

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui

from fixed_joint_mating.mater_lcs import mater_lcs_select_helpers, mater_lcs_single_create_helpers, \
    mater_lcs_array_create_helpers
from fixed_joint_mating.mater_lcs.mater_lcs_array_parameters import Offset, OffsetApplicationCoordinateSystem
from fixed_joint_mating.mater_lcs.mater_lcs_array_create_helpers import extract_selection_inputs
from logger import warn


def run_create(doc: App.Document | None = None):
    if doc is None:
        warn('AvaHelpersWorkbench: no active document.')
        return

    doc.openTransaction('Create mater LCS')
    try:
        mater_lcs_single_create_helpers.create_and_attach(doc)
        doc.commitTransaction()
    except Exception:
        doc.abortTransaction()
        raise
    finally:
        doc.recompute()


def run_create_array(doc: App.Document | None = None):
    if doc is None:
        warn('AvaHelpersWorkbench: no active document.')
        return

    selection = extract_selection_inputs(doc)
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
            self.name_prefix.textChanged.connect(self.preview)
            self.name_prefix.editingFinished.connect(self.preview)
            layout.addRow('Name prefix:', self.name_prefix)

            self.space_between = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
            self.space_between.setProperty('unit', 'mm')
            self.space_between.setProperty('value', App.Units.Quantity(2))
            self.space_between.valueChanged.connect(self.preview)
            layout.addRow('Space between:', self.space_between)

            layout.addRow(QtGui.QLabel(''))  # blank row as a spacer

            self.x_offset = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
            self.y_offset = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
            self.z_offset = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
            for w in (self.x_offset, self.y_offset, self.z_offset):
                w.setProperty('unit', 'mm')
                w.setProperty('value', App.Units.Quantity(0))
                w.valueChanged.connect(self.preview)
            self.global_space_offset = QtGui.QCheckBox('Global')
            self.global_space_offset.setChecked(False)
            self.global_space_offset.stateChanged.connect(self.preview)
            layout.addRow('X offset:', self.x_offset)
            layout.addRow('Y offset:', self.y_offset)
            layout.addRow('Z offset:', self.z_offset)
            layout.addRow('Global:', self.global_space_offset)

            self.doc.openTransaction('Create mater LCS array')
            self.preview()  # Initial launch

        def preview(self, *args):
            self.doc.abortTransaction()
            self.doc.openTransaction('Create mater LCS array')

            name_prefix = self.name_prefix.text()
            length = self.space_between.property('value')
            offset = Offset(
                x=self.x_offset.property('value'),
                y=self.y_offset.property('value'),
                z=self.z_offset.property('value'),
                coordinate_system_application=OffsetApplicationCoordinateSystem.GLOBAL if self.global_space_offset.isChecked() else OffsetApplicationCoordinateSystem.LCS,
            )
            mater_lcs_array_create_helpers.create(doc, selection, name_prefix, length, offset)

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


def run_update_array(doc: App.Document | None = None):
    if doc is None:
        warn('AvaHelpersWorkbench: no active document.')
        return

    mater_lcses = mater_lcs_select_helpers.pull_selected_objects_that_lead_to_mater_lcs()
    mater_lcses = [l.obj for l in mater_lcses]

    doc.openTransaction('Update mater LCS array')
    try:
        mater_lcs_array_create_helpers.update(doc, mater_lcses)
        doc.commitTransaction()
    except Exception:
        doc.abortTransaction()
        raise
    finally:
        doc.recompute()