import FreeCAD as App

from fixed_joint_mating import _fixed_joint_mater
from logger import warn


def run(doc: App.Document | None = None):
    doc = doc or App.ActiveDocument
    if doc is None:
        warn('AvaHelpersWorkbench: no active document.')
        return
    _fixed_joint_mater.toggle_visibility(doc.Objects)
    doc.recompute()
