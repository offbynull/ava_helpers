import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui

from logger import log, error, warn


def _find_matching_face_name(obj, target_face, tol=1e-6):
    target_area = target_face.Area
    target_com = target_face.CenterOfMass
    for i, face in enumerate(obj.Shape.Faces, 1):
        if abs(face.Area - target_area) > tol:
            continue
        if (face.CenterOfMass - target_com).Length > tol:
            continue
        return f'Face{i}'
    raise RuntimeError('Could not remap source face onto body.')

def _run_internal(
        doc: App.Document,
        src: App.DocumentObject,
        src_face_subname: str,
        src_face: App.DocumentObject,
        dst_pocket_length: float,
        dst_label_suffix: str
) -> App.DocumentObject | None:
    body = doc.addObject('PartDesign::Body', src.Label + '_Body')
    body.Label = src.Label + dst_label_suffix

    body.BaseFeature = src

    doc.recompute()

    log(f'Created body: {body.Label}')
    log(f'BaseFeature: {src.Label}')

    if dst_pocket_length < 0:
        error('Negative pocket length')
        return None

    # body_face_subname = _find_matching_face_name(body, src_face)

    pocket = body.newObject('PartDesign::Pocket','Pocket')
    pocket.Profile = (body.BaseFeature, [src_face_subname])
    pocket.Type = 'Length'
    pocket.Length = dst_pocket_length
    body.Tip = pocket

    doc.recompute()

    return body


def run(doc: App.Document) -> None:
    if doc is None:
        warn('AvaHelpersWorkbench: no active document.')
        return

    sel = Gui.Selection.getSelectionEx()
    if len(sel) != 1:
        raise RuntimeError('Select exactly one object.')
    src = sel[0].Object
    src_face_subname = sel[0].SubElementNames[0]  # e.g. "Face3"
    src_face = sel[0].SubObjects[0]  # actual Part.Face

    Gui.Selection.clearSelection()

    class PocketForkerTaskPanel:
        def __init__(self):
            self.form = QtGui.QWidget()
            layout = QtGui.QFormLayout(self.form)

            self.label_suffix = QtGui.QLineEdit()
            self.label_suffix.setText('')
            self.label_suffix.setPlaceholderText('Enter label suffix')
            self.label_suffix.textChanged.connect(self.preview)
            self.label_suffix.editingFinished.connect(self.preview)
            layout.addRow('Label suffix:', self.label_suffix)

            self.pocket_length = Gui.UiLoader().createWidget('Gui::QuantitySpinBox')
            self.pocket_length.setProperty('unit', 'mm')
            self.pocket_length.setProperty('value', App.Units.Quantity(1, 'mm'))
            self.pocket_length.valueChanged.connect(self.preview)
            layout.addRow('Pocket length:', self.pocket_length)

            doc.openTransaction('Pocket fork object')
            self.preview()  # Initial launch

        def preview(self, *args):
            doc.abortTransaction()
            doc.openTransaction('Pocket fork object')

            if hasattr(src, 'ViewObject'):
                src.ViewObject.Visibility = False

            dst_label_suffix = self.label_suffix.text()
            if dst_label_suffix == '':
                dst_label_suffix = f' - {self.pocket_length.property("value")} removed'
            dst_pocket_length = self.pocket_length.property('value').getValueAs('mm').Value
            _run_internal(doc, src, src_face_subname, src_face, dst_pocket_length, dst_label_suffix)
            doc.recompute()

        def accept(self):
            if hasattr(src, 'ViewObject'):
                src.ViewObject.Visibility = True

            doc.commitTransaction()
            Gui.Control.closeDialog()
            return True

        def reject(self):
            doc.abortTransaction()
            Gui.Control.closeDialog()
            return True

    Gui.Control.showDialog(PocketForkerTaskPanel())
