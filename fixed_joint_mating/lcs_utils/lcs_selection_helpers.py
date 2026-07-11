from dataclasses import dataclass

import FreeCAD as App
import FreeCADGui as Gui

from fixed_joint_mating.lcs_utils.lcs_identifier import MATER_LCS_IDENTIFIER
from logger import log


@dataclass
class MaterLCSSelection:
    obj: App.DocumentObject
    selected_path: str


def _obj_desc(o):
    if not o:
        return '<None>'
    return f'<{getattr(o,"TypeId","?")} Name={getattr(o,"Name","?")} Label={getattr(o,"Label","?")}>'


def _find_mater_lcs_in_subname(doc, subname):
    bits = subname.rstrip('.').split('.')

    log(f'subname={subname!r}')
    log(f'bits={bits!r}')

    # Walk right-to-left: child -> parent LCS -> component occurrence
    for i in range(len(bits) - 1, -1, -1):
        name = bits[i]
        obj = doc.getObject(name)

        log(f'checking bit[{i}]={name!r} obj={_obj_desc(obj)}')

        if not obj:
            continue

        if obj.TypeId != 'Part::LocalCoordinateSystem':
            continue

        if MATER_LCS_IDENTIFIER not in obj.PropertiesList:
            log(f'skip non-mater LCS: {_obj_desc(obj)}')
            continue

        lcs_path = '.'.join(bits[:i + 1]) + '.'
        log(f'OK mater LCS path={lcs_path!r}')
        return obj, lcs_path

    log(f'FAIL: no mater LCS found in {subname!r}')
    return None


def pull_selected_objects_that_lead_to_mater_lcs() -> list[MaterLCSSelection]:
    out = []
    seen = set()

    for sel in Gui.Selection.getSelectionEx('', 0):
        log('---- SelectionEx ----')
        log(f'sel.Object={_obj_desc(sel.Object)}')
        log(f'sel.SubElementNames={getattr(sel, "SubElementNames", None)}')
        log(f'sel.SubObjects={getattr(sel, "SubObjects", None)}')

        doc = sel.Object.Document

        for subname in getattr(sel, 'SubElementNames', []) or []:
            ret = _find_mater_lcs_in_subname(doc, subname)
            if not ret:
                continue

            lcs_obj, lcs_path = ret

            if lcs_path in seen:
                continue
            seen.add(lcs_path)

            out.append(MaterLCSSelection(lcs_obj, lcs_path))

    return out
