import FreeCAD as App
import FreeCADGui as Gui
import Part
from PySide import QtGui as QtWidgets

from construction.part_builders._utils import inches_to_feet_inches_str, safe_name

_T_MAX = 23/32
_W_MAX = 4*12
_L_MAX = 8*12
_TONGUE_PROJECTION = 5/16
_TONGUE_THICKNESS = 3/8
PART = '23/32in. x 4 ft. x 8 ft T&G Dryply Plywood (Model # 673014)'


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

        # layout.addRow('Actual thickness:', self.thickness)
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

        varset = doc.addObject('App::VarSet', f'{name}_Parameters')
        varset.Label = f'{label} Parameters'
        varset.addProperty('App::PropertyString', 'Retailer', 'Retail', 'Retailer')
        varset.Retailer = 'Home Depot'
        varset.addProperty('App::PropertyString', 'RetailerPart', 'Retail', 'Retailer Part')
        varset.RetailerPart = PART
        varset.addProperty('App::PropertyLength', 'Length', 'Dimensions', 'Length')
        varset.Length = App.Units.Quantity(l, 'in')
        varset.addProperty('App::PropertyLength', 'Width', 'Dimensions', 'Width')
        varset.Width = App.Units.Quantity(w, 'in')

        z0 = (t - _TONGUE_THICKNESS) / 2

        panel = doc.addObject("Part::Box", f"{name}_Panel")
        panel.Height = App.Units.Quantity(t, 'in')
        panel.setExpression("Length", f"{name}_Parameters.Length")
        panel.setExpression("Width", f"{name}_Parameters.Width")
        tongue = doc.addObject("Part::Box", f"{name}_Tongue")
        tongue.Width = App.Units.Quantity(_TONGUE_PROJECTION, 'in')
        tongue.Height = App.Units.Quantity(_TONGUE_THICKNESS, 'in')
        tongue.setExpression("Length", f"{name}_Parameters.Length")
        tongue.setExpression("Placement.Base.y", f"{name}_Parameters.Width")
        tongue.Placement.Base.z = App.Units.Quantity(z0, 'in')
        groove = doc.addObject("Part::Box", f"{name}_Groove_Cutter")
        groove.Width = App.Units.Quantity(_TONGUE_PROJECTION, 'in')
        groove.Height = App.Units.Quantity(_TONGUE_THICKNESS, 'in')
        groove.setExpression("Length", f"{name}_Parameters.Length")
        groove.Placement.Base.z = App.Units.Quantity(z0, 'in')
        cut = doc.addObject("Part::Cut", f"{name}_Panel_With_Groove")
        cut.Base = panel
        cut.Tool = groove
        fuse = doc.addObject("Part::Fuse", f"{name}_Panel_Tongue_Groove")
        fuse.Base = cut
        fuse.Tool = tongue

        group = doc.addObject("App::DocumentObjectGroup", f"{name}_Group")
        group.Label = f"{label} Group"
        group.addObject(varset)
        group.addObject(fuse)

        return group