import re

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui

from construction.lumber_builders import lumber_2in_x_4in_x_8ft__2_Premium_Grade_KD_HT_Stud_Model__058449, \
    lumber_2in_x_4in_x_10ft__2_Premium_Grade_SPF_Dimensional_Lumber_Model__6091, \
    lumber_6in_x_6in_8ft__2_Pressure_Ground_Contact_Southern_Pine_Timber_Model__260691, \
    lumber_2in_x_4in_x_8ft__2_Ground_Contact_Pressure_Treated_Southern_Yellow_Pine_Lumber_Model__106147
from logger import warn

CUT_GROUP_NAME = 'Construction_materials'
CUT_GROUP_LABEL = 'Construction materials'


PARTS = [
    lumber_2in_x_4in_x_8ft__2_Premium_Grade_KD_HT_Stud_Model__058449,
    lumber_2in_x_4in_x_10ft__2_Premium_Grade_SPF_Dimensional_Lumber_Model__6091,
    lumber_2in_x_4in_x_8ft__2_Ground_Contact_Pressure_Treated_Southern_Yellow_Pine_Lumber_Model__106147,
    lumber_6in_x_6in_8ft__2_Pressure_Ground_Contact_Southern_Pine_Timber_Model__260691,
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
                self.combo.addItem(part.LABEL)

                card = part.Card(self.preview)
                self.cards.append(card)
                self.stack.addWidget(card.form)

            self.combo.currentIndexChanged.connect(self.stack.setCurrentIndex)
            self.combo.currentIndexChanged.connect(self.preview)

            layout.addRow(self.combo)
            layout.addRow(self.stack)

            doc.openTransaction('Create lumber')
            self.preview()  # Initial launch

        def preview(self, *args):
            doc.abortTransaction()
            doc.openTransaction('Create lumber')

            card = self.cards[self.combo.currentIndex()]

            group = get_or_create_cut_group(doc)
            name_prefix = self.name_prefix.text()
            _, name = card.label_and_name(name_prefix)
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