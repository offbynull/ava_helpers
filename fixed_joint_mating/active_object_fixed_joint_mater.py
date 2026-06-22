import FreeCAD as App

from fixed_joint_mating import _fixed_joint_mater
from logger import warn
from utils import get_all_descendants_under_active_object


def run(doc: App.Document | None = None):
    doc = doc or App.ActiveDocument
    if doc is None:
        warn('AvaHelpersWorkbench: no active document.')
        return
    objects = get_all_descendants_under_active_object(doc)
    _fixed_joint_mater.clock(objects)
    doc.recompute()
