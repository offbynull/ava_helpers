import FreeCAD as App
import FreeCADGui as Gui

from logger import log


def run(doc: App.Document | None = None) -> None:
    sel = Gui.Selection.getSelection()
    if len(sel) != 1:
        raise RuntimeError('Select exactly one object.')

    src = sel[0]

    if not hasattr(src, 'Shape'):
        raise RuntimeError('Selected object has no Shape.')

    body = doc.addObject('PartDesign::Body', src.Label + '_Body')
    body.Label = src.Label

    body.BaseFeature = src

    if hasattr(src, 'ViewObject'):
        src.ViewObject.Visibility = False

    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(body)

    doc.recompute()

    log(f'Created body: {body.Label}')
    log(f'BaseFeature: {src.Label}')
