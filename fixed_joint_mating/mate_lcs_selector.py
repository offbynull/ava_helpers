import re

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui

from fixed_joint_mating.selection import selectable_enumerator
from logger import warn, error


def run(doc: App.Document | None = None):
    if doc is None:
        warn('AvaHelpersWorkbench: no active document.')
        return

    class SelectTaskPanel:
        def __init__(self):
            self.form = QtGui.QWidget()
            layout = QtGui.QFormLayout(self.form)

            intro = QtGui.QLabel(
                'Pattern 1 selected first, followed by pattern 2.\n'
            )
            intro.setWordWrap(True)
            layout.addWidget(intro)

            self.label_flag = QtGui.QCheckBox('Label')
            self.label_flag.setChecked(True)
            self.label_flag.stateChanged.connect(self.preview)

            self.pattern1 = QtGui.QLineEdit()
            self.pattern1.setText('(?i).*')
            self.pattern1.setPlaceholderText('Enter regex pattern')
            self.pattern1.editingFinished.connect(self.preview)
            layout.addRow('Pattern 1:', self.pattern1)

            self.list1 = QtGui.QListWidget()
            self.list1.clear()
            self.list1.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
            layout.addWidget(self.list1)

            self.pattern2 = QtGui.QLineEdit()
            self.pattern2.setText('(?i).*')
            self.pattern2.setPlaceholderText('Enter regex pattern')
            self.pattern2.editingFinished.connect(self.preview)
            layout.addRow('Pattern 2:', self.pattern2)

            self.list2 = QtGui.QListWidget()
            self.list2.clear()
            self.list2.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
            layout.addWidget(self.list2)

            # doc.openTransaction('Select')
            self.preview()  # Initial launch

        def preview(self, *args):
            # doc.abortTransaction()
            # doc.openTransaction('Select')

            pattern1 = re.compile(self.pattern1.text())
            pattern2 = re.compile(self.pattern2.text())

            selectable_items = selectable_enumerator.run(doc)
            found1_list = []
            found2_list = []
            for item in selectable_items:
                found1 = pattern1.search(item.to_friendly_string())
                found2 = pattern2.search(item.to_friendly_string())
                if found1 and found2:
                    warn(f'Found with both patterns: {item.to_friendly_string()}')
                if found1:
                    found1_list.append(item)
                if found2:
                    found2_list.append(item)
            self.list1.clear()
            self.list1.addItems([f.to_friendly_string() for f in found1_list])
            self.list2.clear()
            self.list2.addItems([f.to_friendly_string() for f in found2_list])

            Gui.Selection.clearSelection()
            total_found_list = found1_list + found2_list
            if len(total_found_list) > 150:
                error('Found more than 150 items in list - preventing selection.')
            else:
                for found in total_found_list:
                    Gui.Selection.addSelection(*found.to_selection_tuple())

            # doc.recompute()

        def accept(self):
            # doc.commitTransaction()
            Gui.Control.closeDialog()
            return True

        def reject(self):
            # doc.abortTransaction()
            Gui.Selection.clearSelection()
            Gui.Control.closeDialog()
            return True

    Gui.Control.showDialog(SelectTaskPanel())
