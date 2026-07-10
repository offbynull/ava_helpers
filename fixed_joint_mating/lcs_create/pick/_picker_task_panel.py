from typing import Callable

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui

from logger import log


class PickerTaskPanel:
    def __init__(
            self,
            abort_callback: Callable,
            confirm_callback: Callable,
            update_callback: Callable,
            default_name: str,
            default_snap_xy: App.Units.Quantity,
            edge_x_axis_length_mm: App.Units.Quantity
    ):
        self.doc = App.ActiveDocument

        self.abort_callback = abort_callback
        self.confirm_callback = confirm_callback
        self.update_callback = update_callback

        self.form = QtGui.QWidget()
        layout = QtGui.QFormLayout(self.form)

        self.name = QtGui.QLineEdit()
        self.name.setText(default_name)
        self.name.setPlaceholderText('Enter name')
        self.name.editingFinished.connect(self.preview)
        layout.addRow('Name prefix:', self.name)

        self.snap_x = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.snap_x.setProperty('value', default_snap_xy)
        self.snap_x.editingFinished.connect(self.snap_x_update_preview)
        layout.addRow('Snap X:', self.snap_x)

        self.snap_y = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.snap_y.setProperty('value', default_snap_xy)
        self.snap_y.editingFinished.connect(self.preview)
        layout.addRow('Snap Y:', self.snap_y)

        layout.addRow("", QtGui.QWidget())

        self.edge_x_axis_length_mm = edge_x_axis_length_mm
        self.snap_x_subdivision = QtGui.QDoubleSpinBox()
        self.snap_x_subdivision.setValue(0.0)
        self.snap_x_subdivision.setMinimum(0.0)
        self.snap_x_subdivision.editingFinished.connect(self.snap_x_subdiv_update_preview)
        layout.addRow('Snap X Subdivision:', self.snap_x_subdivision)

        self.preview()  # Initial launch

    def snap_x_update_preview(self, *args):
        self.snap_x_subdivision.setValue(0.0)
        self.preview()

    def snap_x_subdiv_update_preview(self, *args):
        if self.snap_x_subdivision.value() > 0:
            log(f'{self.edge_x_axis_length_mm / self.snap_x_subdivision.value()=}')
            self.snap_x.setProperty(
                'value',
                App.Units.Quantity(
                    self.edge_x_axis_length_mm / self.snap_x_subdivision.value(),
                    'mm'
                )
            )
        self.preview()

    def preview(self, *args):
        name = self.name.text()
        snap_x = self.snap_x.property('value')
        snap_y = self.snap_y.property('value')
        self.update_callback(name, snap_x, snap_y)

    def accept(self):
        self.confirm_callback()
        return True

    def reject(self):
        self.abort_callback()
        return True
