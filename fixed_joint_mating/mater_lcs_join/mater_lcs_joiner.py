import os
import sys

import FreeCAD as App
import FreeCADGui as Gui

from fixed_joint_mating.mater_lcs.mater_lcs_select_helpers import MaterLCSSelection
from logger import error, log

asm_path = os.path.join(App.getHomePath(), 'Mod', 'Assembly')
if asm_path not in sys.path:
    sys.path.append(asm_path)

import UtilsAssembly
import JointObject


def get_component_ref_from_mater_lcs(asm, mater):
    for parent, path in mater.parents:
        log(f'{parent=} {path=} vs {mater=}')
        if parent == asm:
            return UtilsAssembly.getComponentReference(asm, parent, path)
    return None, ''


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

    joint_group.purgeTouched()
    asm.purgeTouched()

    JointObject.Joint(joint, 0)          # 0 = Fixed
    JointObject.ViewProviderJoint(joint.ViewObject)

    joint.Proxy.setJointConnectors(
        joint,
        [
            [part_a, [sub_a, sub_a]],
            [part_b, [sub_b, sub_b]],
        ]
    )

    joint.purgeTouched()
    asm.recompute(True)

    Gui.Selection.clearSelection()

    log(f'Created fixed joint: {joint.Name}')

    return joint