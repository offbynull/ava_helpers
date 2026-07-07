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

        self.snap_xy = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.snap_xy.setProperty('value', default_snap_xy)
        self.snap_xy.editingFinished.connect(self.preview)
        layout.addRow('Snap XY:', self.snap_xy)

        self.preview()  # Initial launch

    def preview(self, *args):
        name = self.name.text()
        snap_xy = self.snap_xy.property('value')
        self.update_callback(name, snap_xy)

    def accept(self):
        self.confirm_callback()
        return True

    def reject(self):
        self.abort_callback()
        return True
