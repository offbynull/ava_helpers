# https://chatgpt.com/share/6a394267-8320-83ea-8eeb-6978b4bc0678

import FreeCAD as App
import FreeCADGui as Gui

from logger import log


def run(doc: App.Document | None = None) -> None:
    sel = Gui.Selection.getSelection()
    if len(sel) != 1:
        raise Exception("Select exactly one object.")
    obj, = sel

    bb = obj.Shape.BoundBox

    translation = App.Vector(
        -bb.Center.x,
        -bb.Center.y,
        -bb.Center.z
    )

    obj.Placement.Base = obj.Placement.Base + translation

    App.ActiveDocument.recompute()

    log("Done: object centered at origin.")