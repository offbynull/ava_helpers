import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui as QtWidgets

from construction.lumber_builders._utils import inches_to_feet_inches_str, safe_name

_T_MAX = 1.5
_W_MAX = 3.5
_L_MAX = 96
LABEL = '2 in. x 4 in. x 8 ft. #2 Premium Grade KD-HT Stud (Model # 058449)'


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

    def label_and_name(self, prefix: str):
        t, w, l = self._dimensions()
        label = ''
        if abs(t - _T_MAX) > 10e-4 or abs(w - _W_MAX) > 10e-4 or abs(l - _L_MAX) > 10e-4:
            label = f'{inches_to_feet_inches_str(t)} x ' \
                    + f'{inches_to_feet_inches_str(w)} x ' \
                    + f'{inches_to_feet_inches_str(l)} ----- '
        label = f'{label}{LABEL}'
        return prefix + ' ' + label, safe_name(prefix + ' ' +label)

    def build(self, doc: App.Document, prefix: str):
        t, w, l = self._dimensions()
        label, name = self.label_and_name(prefix)

        body = doc.addObject('PartDesign::Body', name)
        body.Label = label
        body.addProperty('App::PropertyString', 'Retailer', 'Retail', 'Retailer')
        body.setEditorMode('Retailer', 1)
        body.Retailer = 'Home Depot'
        body.addProperty('App::PropertyString', 'RetailerPart', 'Retail', 'Retailer Part')
        body.setEditorMode('RetailerPart', 1)
        body.RetailerPart = LABEL
        body.addProperty('App::PropertyLength', 'Length', 'Dimensions', 'Length')
        body.setEditorMode('Length', 1)
        body.addProperty('App::PropertyLength', 'Width', 'Dimensions', 'Width')
        body.setEditorMode('Width', 1)
        body.addProperty('App::PropertyLength', 'Thickness', 'Dimensions', 'Thickness')
        body.setEditorMode('Thickness', 1)

        box = body.newObject('PartDesign::AdditiveBox', 'AdditiveBox')
        box.Length = App.Units.Quantity(l, 'in')
        box.Width = App.Units.Quantity(w, 'in')
        box.Height = App.Units.Quantity(t, 'in')
        body.Tip = box

        body.setExpression('Length', f'{box.Name}.Length')
        body.setExpression('Width', f'{box.Name}.Width')
        body.setExpression('Thickness', f'{box.Name}.Height')

        return body