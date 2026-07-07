import os
import sys

import FreeCAD as App
import FreeCADGui as Gui

from fixed_joint_mating.lcs_utils.lcs_selection_helpers import MaterLCSSelection
from logger import error, log

asm_path = os.path.join(App.getHomePath(), 'Mod', 'Assembly')
if asm_path not in sys.path:
    sys.path.append(asm_path)

import UtilsAssembly
import JointObject


def _obj_desc(o):
    if not o:
        return "<None>"
    return (
        f"<{getattr(o, 'TypeId', '?')} "
        f"Name={getattr(o, 'Name', '?')} "
        f"Label={getattr(o, 'Label', '?')}>"
    )


def get_component_ref_from_mater_lcs(asm, mater):
    log("---- get_component_ref_from_mater_lcs ----")
    log(f"asm={_obj_desc(asm)}")
    log(f"mater.obj={_obj_desc(mater.obj)}")
    log(f"mater.selected_path={getattr(mater, 'selected_path', None)!r}")

    selected_path = getattr(mater, "selected_path", "") or ""
    path = selected_path.rstrip(".")

    if not path:
        log("FAIL: empty selected_path")
        return None, ""

    comp_name, sep, sub = path.partition(".")
    log(f"parsed comp_name={comp_name!r} sub={sub!r}")

    if not sep or not sub:
        log("FAIL: selected_path does not contain component + subpath")
        return None, ""

    group = list(getattr(asm, "Group", []) or [])
    log("asm.Group:")
    for o in group:
        log(f"  {_obj_desc(o)}")

    comp = next((o for o in group if o.Name == comp_name), None)

    if not comp:
        log(f"FAIL: no asm.Group object named {comp_name!r}")
        doc = getattr(asm, "Document", None)
        if doc:
            doc_obj = doc.getObject(comp_name)
            log(f"doc.getObject({comp_name!r})={_obj_desc(doc_obj)}")
        return None, ""

    subname = sub + "."
    log(f"OK: component={_obj_desc(comp)} subname={subname!r}")

    ret = (comp, subname)
    log(f"returning ret={ret}")
    return ret


def run(
        doc: App.Document,
        mater_lcs_a: MaterLCSSelection,
        mater_lcs_b: MaterLCSSelection
) -> App.DocumentObject:
    asm = UtilsAssembly.activeAssembly()
    if not asm:
        error('No active assembly.')
        return None

    log(f'{mater_lcs_a=}')
    log(f'{mater_lcs_b=}')

    part_a, sub_a = get_component_ref_from_mater_lcs(asm, mater_lcs_a)
    part_b, sub_b = get_component_ref_from_mater_lcs(asm, mater_lcs_b)

    if not part_a or not part_b:
        error('No reference to mater LCSes in the active assembly.')
        return None

    asm.ensureIdentityPlacements()

    joint_group = UtilsAssembly.getJointGroup(asm)
    joint = joint_group.newObject('App::FeaturePython', 'Joint')
    joint.Label = 'MaterLCS_FixedJoint'

    JointObject.Joint(joint, 0)          # 0 = Fixed
    JointObject.ViewProviderJoint(joint.ViewObject)

    joint.Proxy.setJointConnectors(
        joint,
        [
            [part_a, [sub_a, sub_a]],
            [part_b, [sub_b, sub_b]],
        ]
    )

    Gui.Selection.clearSelection()

    log(f'Created fixed joint: {joint.Name}')

    return joint