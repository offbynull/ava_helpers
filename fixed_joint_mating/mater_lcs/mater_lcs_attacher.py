# https://chatgpt.com/share/6a42a9e0-db78-83ea-ab2f-014d58f4ae50
import FreeCAD as App
import FreeCADGui as Gui

from logger import log


def run(doc: App.Document, mater_lcs: App.DocumentObject, obj: App.DocumentObject, obj_face_name: str, obj_vertex_name: str):
    support = [(obj, obj_face_name), (obj, obj_vertex_name)]

    if hasattr(mater_lcs, 'AttachmentSupport'):
        mater_lcs.AttachmentSupport = support
    else:
        mater_lcs.Support = support

    mater_lcs.MapMode = 'TangentPlane'
    mater_lcs.MapReversed = False

    if hasattr(mater_lcs, 'AttachmentOffset'):
        mater_lcs.AttachmentOffset = App.Placement()

    doc.recompute()

    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(mater_lcs)

    log(f'Attached {mater_lcs.Label}')

# run()
