from dataclasses import dataclass

import FreeCAD as App
import FreeCADGui as Gui

from fixed_joint_mating.mater_lcs.mater_lcs_identifier import MATER_LCS_IDENTIFIER


@dataclass
class MaterLCSSelection:
    obj: App.DocumentObject
    parents: list[tuple[App.Document, str]]


def _walk_up_to_lcs_object(obj, seen=None, level=0):
    if obj is None:
        return None
    if seen is None:
        seen = set()
    if obj.Name in seen:
        return None
    seen.add(obj.Name)
    if obj.TypeId == 'Part::LocalCoordinateSystem':
        return obj, level
    for parent in getattr(obj, 'InList', []):
        ret = _walk_up_to_lcs_object(parent, seen, level + 1)
        if ret:
            return ret
    return None


def pull_selected_objects_that_lead_to_mater_lcs() -> list[MaterLCSSelection]:
    out = []
    seen = set()

    for sel in Gui.Selection.getSelectionEx():
        walk_res = _walk_up_to_lcs_object(sel.Object)
        if walk_res is None:
            continue
        lcs_obj, skip_cnt = walk_res
        if lcs_obj in seen:
            continue
        if MATER_LCS_IDENTIFIER not in lcs_obj.PropertiesList:
            continue
        seen.add(lcs_obj)
        out.append(MaterLCSSelection(lcs_obj, lcs_obj.Parents))
    return out
