import FreeCAD as App

from fixed_joint_mating import _fixed_joint_mater
from utils import get_all_descendants_under_active_object


def run(doc: App.Document | None = None):
    objects = get_all_descendants_under_active_object(doc)
    _fixed_joint_mater.run(objects)
    doc.recompute()
