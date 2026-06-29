import string
import random

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui

from fixed_joint_mating import _single_mater_lcs, _array_mater_lcs
from logger import warn


def run_single(doc: App.Document | None = None):
    doc = doc or App.ActiveDocument
    if doc is None:
        warn('AvaHelpersWorkbench: no active document.')
        return

    doc.openTransaction('Create mater LCS')
    try:
        _single_mater_lcs.run(doc)
        doc.commitTransaction()
    except Exception:
        doc.abortTransaction()
        raise
    finally:
        doc.recompute()


def run_array(doc: App.Document | None = None):
    doc = doc or App.ActiveDocument
    if doc is None:
        warn('AvaHelpersWorkbench: no active document.')
        return

    # doc.openTransaction('Create mater LCS')
    # try:
    #     _array_mater_lcs.run(doc)
    #     doc.commitTransaction()
    # except Exception:
    #     doc.abortTransaction()
    #     raise
    # finally:
    #     doc.recompute()

    selection = _array_mater_lcs.extract_selection(doc)
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

            self.doc.openTransaction('Array mater LCS')
            self.preview()  # Initial launch

        def preview(self, *args):
            self.doc.abortTransaction()
            self.doc.openTransaction('Array mater LCS')

            name_prefix = self.name_prefix.text()
            length = self.space_between.property('value')
            offset = _array_mater_lcs.Offset(
                x=self.x_offset.property('value'),
                y=self.y_offset.property('value'),
                z=self.z_offset.property('value'),
                coordinate_system_application=_array_mater_lcs.OffsetApplicationCoordinateSystem.GLOBAL if self.global_space_offset.isChecked() else _array_mater_lcs.OffsetApplicationCoordinateSystem.LCS,
            )
            _array_mater_lcs.execute(doc, selection, name_prefix, length, offset)

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