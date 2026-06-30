# https://chatgpt.com/share/6a42a9e0-db78-83ea-ab2f-014d58f4ae50
import FreeCAD as App
import FreeCADGui as Gui

from logger import log, warn


def run(doc: App.Document, mater_lcs: App.DocumentObject):
    if hasattr(mater_lcs, 'AttachmentSupport'):
        mater_lcs.AttachmentSupport = None
    else:
        mater_lcs.Support = None

    warn('Detached from object due to cycle (see https://github.com/FreeCAD/FreeCAD/issues/31091)')
    
    doc.recompute()

    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(mater_lcs)

    log(f'Detached {mater_lcs.Label}')

# run()
