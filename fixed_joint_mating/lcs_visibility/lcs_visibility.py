import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui

from fixed_joint_mating.lcs_utils import lcs_visibility_changer
from logger import warn


def run_change(doc: App.Document | None = None):
    if doc is None:
        warn('AvaHelpersWorkbench: no active document.')
        return

    class VisibilityChangerTaskPanel:
        def __init__(self):
            self.doc = App.ActiveDocument

            self.form = QtGui.QWidget()
            layout = QtGui.QFormLayout(self.form)

            self.label_regex = QtGui.QLineEdit()
            self.label_regex.setText('.*')
            self.label_regex.editingFinished.connect(self.preview)
            # self.label_regex.textChanged.connect(self.preview)
            layout.addRow('Label path regex:', self.label_regex)

            self.name_regex = QtGui.QLineEdit()
            self.name_regex.setText('.*')
            self.name_regex.editingFinished.connect(self.preview)
            # self.name_regex.textChanged.connect(self.preview)
            layout.addRow('Name path regex:', self.name_regex)

            layout.addRow(QtGui.QLabel(''))  # blank row as a spacer

            self.visible = QtGui.QCheckBox()
            self.visible.setChecked(True)
            self.visible.stateChanged.connect(self.preview)
            layout.addRow('Visible:', self.visible)

            self.label_parents_cache = {}
            self.name_parents_cache = {}

            self.doc.openTransaction('Change mater LCS visibility')
            self.preview()  # Initial launch

        def preview(self, *args):
            self.doc.abortTransaction()
            self.doc.openTransaction('Change mater LCS visibility')

            label_regex = self.label_regex.text()
            name_regex = self.name_regex.text()
            visible = self.visible.isChecked()
            lcs_visibility_changer.change(doc, visible, self.label_parents_cache, self.name_parents_cache, label_regex, name_regex)

            self.doc.recompute()

        def accept(self):
            self.doc.commitTransaction()
            Gui.Control.closeDialog()
            return True

        def reject(self):
            self.doc.abortTransaction()
            Gui.Control.closeDialog()
            return True

    Gui.Control.showDialog(VisibilityChangerTaskPanel())


def run_hide_all(doc: App.Document | None = None):
    if doc is None:
        warn('AvaHelpersWorkbench: no active document.')
        return

    doc.openTransaction('Change mater LCS visibility')
    try:
        lcs_visibility_changer.change(doc, False, {}, {}, '.*', '.*')
        doc.commitTransaction()
    except Exception:
        doc.abortTransaction()
        raise
    finally:
        doc.recompute()


def run_show_all(doc: App.Document | None = None):
    if doc is None:
        warn('AvaHelpersWorkbench: no active document.')
        return

    doc.openTransaction('Change mater LCS visibility')
    try:
        lcs_visibility_changer.change(doc, True, {}, {}, '.*', '.*')
        doc.commitTransaction()
    except Exception:
        doc.abortTransaction()
        raise
    finally:
        doc.recompute()

