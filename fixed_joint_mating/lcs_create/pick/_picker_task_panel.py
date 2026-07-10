from typing import Callable

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui


class PickerTaskPanel:
    def __init__(
            self,
            abort_callback: Callable,
            confirm_callback: Callable,
            update_callback: Callable,
            default_name: str,
            default_snap_xy: App.Units.Quantity
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
        self.snap_x.editingFinished.connect(self.preview)
        layout.addRow('Snap X:', self.snap_x)

        self.snap_y = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.snap_y.setProperty('value', default_snap_xy)
        self.snap_y.editingFinished.connect(self.preview)
        layout.addRow('Snap Y:', self.snap_y)

        self.preview()  # Initial launch

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
