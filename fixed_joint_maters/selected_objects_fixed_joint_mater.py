import FreeCAD as App

from fixed_joint_maters import _fixed_joint_mater
from utils import get_all_descendants_under_selected_objects


def run(doc: App.Document | None = None):
    objects = get_all_descendants_under_selected_objects(doc)
    _fixed_joint_mater.run(objects)
    doc.recompute()
