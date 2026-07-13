import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui

from construction.part_builders import part_2in_x_4in_x_8ft__2_Premium_Grade_KD_HT_Stud_Model__058449, \
    part_2in_x_4in_x_10ft__2_Premium_Grade_SPF_Dimensional_Lumber__Model__6091, \
    part_6in_x_6in_8ft__2_Pressure_Ground_Contact_Southern_Pine_Timber__Model__260691, \
    part_4in_x_8in_x_16in_Solid_Concrete_Block__Model__30168621, \
    part_4in_x_4in_x_10ft__2_Pressure_Treated_Ground_Contact_Southern_Pine_Wood_Post__Model__4220254, \
    part_2in_x_4in_x_8ft__2_Ground_Contact_Pressure_Treated_Southern_Yellow_Pine_Lumber__Model__106147, \
    part_2in_x_6in_x_10ft__1_Ground_Contact_Pressure_Treated_Southern_Yellow_Pine_Lumber__Model__253905, \
    part_2in_x_8in_x_8ft__1_Ground_Contact_Pressure_Treated_Southern_Yellow_Pine_Lumber__Model__106004, \
    part_2in_x_8in_x_10ft__1_Ground_Contact_Pressure_Treated_Southern_Yellow_Pine_Lumber__Model__106004, \
    part_2in_x_8in_x_8ft__2_Premium_Grade_Fir_Dimensional_Lumber__Model__769887252895, \
    part_2in_x_10in_x_8ft__2_Premium_Grade_Fir_Dimensional_Lumber__Model__915564, \
    part_2in_x_8in_x_10ft__2_Premium_Grade_Fir_Dimensional_Lumber__Model__604364, \
    part_15_32in_x_4ft_x_8ft_Sheathing_Plywood__Model__20159, part_23_32in_x_4ft_x_8ft_T_G_Dryply_Plywood_Model__673014, \
    part_TP_3_1_8in_x_9in_20_Gauge_Galvanized_Tie_Plate__Model__TP39, \
    part_2in_x_6in_x_8ft_No_2_Prime_Pressure_Treated_Ground_Contact_Southern_Pine_Lumber__Model__2311255, \
    part_2in_x_6in_x_8ft__1_Ground_Contact_Pressure_Treated_Southern_Yellow_Pine_Lumber__Model__253905, \
    part_2in_x_6in_x_12ft__1_Ground_Contact_Pressure_Treated_Southern_Yellow_Pine_Lumber__Model__253905, \
    part_2in_x_6in_x_16ft__1_Ground_Contact_Pressure_Treated_Southern_Yellow_Pine_Lumber__Model__253905, \
    part_4in_x_6in_x_8ft__2_Ground_Contact_Pressure_Treated_Timber__Model__259270, \
    part_4in_x_6in_x_12ft__2_Ground_Contact_Pressure_Treated_Timber__Model__288746, \
    part_2in_x_12in_x_8ft__2_Premium_Grade_Fir_Dimensional_Lumber__Model__707195, \
    part_1_2in_x_4ft_x_8ft_CDX_Ground_Contact_Pressure_Treated_Pine_Plywood__Model__131876
from logger import warn

CUT_GROUP_NAME = 'Construction_materials'
CUT_GROUP_LABEL = 'Construction materials'


PARTS = [
    part_2in_x_4in_x_8ft__2_Premium_Grade_KD_HT_Stud_Model__058449,
    part_2in_x_4in_x_10ft__2_Premium_Grade_SPF_Dimensional_Lumber__Model__6091,
    part_2in_x_8in_x_8ft__2_Premium_Grade_Fir_Dimensional_Lumber__Model__769887252895,
    part_2in_x_8in_x_10ft__2_Premium_Grade_Fir_Dimensional_Lumber__Model__604364,
    part_2in_x_10in_x_8ft__2_Premium_Grade_Fir_Dimensional_Lumber__Model__915564,
    part_2in_x_12in_x_8ft__2_Premium_Grade_Fir_Dimensional_Lumber__Model__707195,
    part_4in_x_4in_x_10ft__2_Pressure_Treated_Ground_Contact_Southern_Pine_Wood_Post__Model__4220254,
    part_6in_x_6in_8ft__2_Pressure_Ground_Contact_Southern_Pine_Timber__Model__260691,
    part_2in_x_4in_x_8ft__2_Ground_Contact_Pressure_Treated_Southern_Yellow_Pine_Lumber__Model__106147,
    part_2in_x_6in_x_8ft_No_2_Prime_Pressure_Treated_Ground_Contact_Southern_Pine_Lumber__Model__2311255,
    part_2in_x_6in_x_8ft__1_Ground_Contact_Pressure_Treated_Southern_Yellow_Pine_Lumber__Model__253905,
    part_2in_x_6in_x_10ft__1_Ground_Contact_Pressure_Treated_Southern_Yellow_Pine_Lumber__Model__253905,
    part_2in_x_6in_x_12ft__1_Ground_Contact_Pressure_Treated_Southern_Yellow_Pine_Lumber__Model__253905,
    part_2in_x_6in_x_16ft__1_Ground_Contact_Pressure_Treated_Southern_Yellow_Pine_Lumber__Model__253905,
    part_2in_x_8in_x_8ft__1_Ground_Contact_Pressure_Treated_Southern_Yellow_Pine_Lumber__Model__106004,
    part_2in_x_8in_x_10ft__1_Ground_Contact_Pressure_Treated_Southern_Yellow_Pine_Lumber__Model__106004,
    part_4in_x_6in_x_8ft__2_Ground_Contact_Pressure_Treated_Timber__Model__259270,
    part_4in_x_6in_x_12ft__2_Ground_Contact_Pressure_Treated_Timber__Model__288746,
    part_1_2in_x_4ft_x_8ft_CDX_Ground_Contact_Pressure_Treated_Pine_Plywood__Model__131876,
    part_15_32in_x_4ft_x_8ft_Sheathing_Plywood__Model__20159,
    part_23_32in_x_4ft_x_8ft_T_G_Dryply_Plywood_Model__673014,
    part_4in_x_8in_x_16in_Solid_Concrete_Block__Model__30168621,
    part_TP_3_1_8in_x_9in_20_Gauge_Galvanized_Tie_Plate__Model__TP39
]


def get_or_create_cut_group(doc):
    group = doc.getObject(CUT_GROUP_NAME)
    if not group:
        group = doc.addObject('App::DocumentObjectGroup', CUT_GROUP_NAME)
        group.Label = CUT_GROUP_LABEL
    return group


def run(doc: App.Document) -> None:
    if doc is None:
        warn('AvaHelpersWorkbench: no active document.')
        return

    class LumberCutTaskPanel:
        def __init__(self):
            self.form = QtGui.QWidget()

            self.form = QtGui.QWidget()
            layout = QtGui.QFormLayout(self.form)
            
            self.combo = QtGui.QComboBox()
            self.stack = QtGui.QStackedWidget()
            self.cards = []

            self.name_prefix = QtGui.QLineEdit()
            self.name_prefix.setText('')
            self.name_prefix.setPlaceholderText('Enter name prefix')
            self.name_prefix.editingFinished.connect(self.preview)
            layout.addRow('Name prefix:', self.name_prefix)

            for part in PARTS:
                self.combo.addItem(part.PART)

                card = part.Card(self.preview)
                self.cards.append(card)
                self.stack.addWidget(card.form)

            self.combo.currentIndexChanged.connect(self.stack.setCurrentIndex)
            self.combo.currentIndexChanged.connect(self.preview)

            layout.addRow(self.combo)
            layout.addRow(self.stack)

            doc.openTransaction('Create part')
            self.preview()  # Initial launch

        def preview(self, *args):
            doc.abortTransaction()
            doc.openTransaction('Create part')

            card = self.cards[self.combo.currentIndex()]

            group = get_or_create_cut_group(doc)
            name_prefix = self.name_prefix.text()
            name = card.name(name_prefix)
            obj = doc.getObject(name)
            if obj is None:
                obj = card.build(doc, name_prefix)
                group.addObject(obj)

            Gui.Selection.clearSelection()
            Gui.Selection.addSelection(obj.Document.Name, obj.Name)

            doc.recompute()

        def accept(self):
            doc.commitTransaction()
            Gui.Control.closeDialog()
            return True

        def reject(self):
            doc.abortTransaction()
            Gui.Control.closeDialog()
            return True

    Gui.Control.showDialog(LumberCutTaskPanel())