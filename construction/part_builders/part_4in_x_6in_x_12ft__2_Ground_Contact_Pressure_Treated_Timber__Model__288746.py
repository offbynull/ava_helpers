import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui as QtWidgets

from construction.part_builders._utils import inches_to_feet_inches_str, safe_name
from construction.part_builders._lumber_cut_creator import create_uneased_slab

_T_MAX = 1.5
_W_MAX = 5.5
_L_MAX = 12*12
PART = '4 in. x 6 in. x 12 ft. #2 Ground Contact Pressure-Treated Timber (Model # 288746)'


class Card:
    def __init__(self, preview):
        self.form = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(self.form)

        self.thickness = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.thickness.setProperty('unit', 'in')
        self.thickness.setProperty('value', App.Units.Quantity(_T_MAX, 'in'))
        self.thickness.editingFinished.connect(preview)

        self.width = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.width.setProperty('unit', 'in')
        self.width.setProperty('value', App.Units.Quantity(_W_MAX, 'in'))
        self.width.editingFinished.connect(preview)

        self.length = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
        self.length.setProperty('unit', 'in')
        self.length.setProperty('value', App.Units.Quantity(_L_MAX, 'in'))
        self.length.editingFinished.connect(preview)

        layout.addRow('Actual thickness:', self.thickness)
        layout.addRow('Actual width:', self.width)
        layout.addRow('Actual length:', self.length)

    def _dimensions(self):
        t = self.thickness.property('value').getValueAs('in').Value
        if t < 0:
            t = _T_MAX + t
        w = self.width.property('value').getValueAs('in').Value
        if w < 0:
            w = _W_MAX + w
        l = self.length.property('value').getValueAs('in').Value
        if l < 0:
            l = _L_MAX + l

        if t <= 0 or w <= 0 or l <= 0:
            raise ValueError('All dimensions must be greater than zero')

        return t, w, l

    def label(self, prefix: str):
        t, w, l = self._dimensions()
        label = ''
        if abs(t - _T_MAX) > 10e-4 or abs(w - _W_MAX) > 10e-4 or abs(l - _L_MAX) > 10e-4:
            label = f'{inches_to_feet_inches_str(t)} x ' \
                    + f'{inches_to_feet_inches_str(w)} x ' \
                    + f'{inches_to_feet_inches_str(l)} ----- '
        label = f'{label}{PART}'
        return prefix + ' ' + label

    def name(self, prefix: str):
        return safe_name(f'{prefix} {self.label(prefix)}')

    def build(self, doc: App.Document, prefix: str):
        t, w, l = self._dimensions()
        name = self.name(prefix)
        label = self.label(prefix)
        return create_uneased_slab(doc, name, label, 'Home Depot', PART, t, w, l)