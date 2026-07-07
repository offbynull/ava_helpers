import FreeCAD as App

from fixed_joint_mating.lcs_utils import lcs_selection_helpers
from fixed_joint_mating.lcs_join import _joiner, _clocker
from logger import error, warn

import UtilsAssembly


def run_single(doc: App.Document) -> App.DocumentObject | None:
    doc.recompute()  # Ensure geometry up to date

    if doc is None:
        warn('AvaHelpersWorkbench: no active document.')
        return

    doc.openTransaction('Join mater LCS')
    try:
        mater_lcses = lcs_selection_helpers.pull_selected_objects_that_lead_to_mater_lcs()
        if len(mater_lcses) != 2:
            error('Select exactly two mater LCSes.')
            return None

        joint = _joiner.run(doc, mater_lcses[0], mater_lcses[1])
        if joint is None:
            return None
        _clocker.run(joint)

        # If I don't have all of this here, it'll do all kinds of weird broken reorientations that will never go back to
        # normal unless I go into the brokenly oriented joint and start perturbing settings (e.g., -1 rotation then +1
        # rotation).
        asm = UtilsAssembly.activeAssembly()
        if not asm:
            error('No active assembly.')
            return None
        joint.Proxy.updateJCSPlacements(joint)
        joint.Proxy.preSolve(joint, False)
        asm.solve(True)
        doc.recompute()

        doc.commitTransaction()
        return joint
    except Exception:
        doc.abortTransaction()
        raise
    finally:
        doc.recompute()


def run_multi(doc: App.Document) -> list[App.DocumentObject] | None:
    doc.recompute()  # Ensure geometry up to date

    if doc is None:
        warn('AvaHelpersWorkbench: no active document.')
        return

    doc.openTransaction('Join mater LCS')
    try:
        mater_lcses = lcs_selection_helpers.pull_selected_objects_that_lead_to_mater_lcs()
        if len(mater_lcses) < 2:
            error('Select >= two mater LCSes.')
            return None

        if len(mater_lcses) % 2 != 0:
            error('Number of selected mater LCSes must be divisibly by 2.')
            return None

        asm = UtilsAssembly.activeAssembly()
        if not asm:
            error('No active assembly.')
            return None
        ret = []
        mater_lcses_a = mater_lcses[:len(mater_lcses) // 2]
        mater_lcses_b = mater_lcses[len(mater_lcses) // 2:]
        for mater_lcs_a, mater_lcs_b in zip(mater_lcses_a, mater_lcses_b):
            joint = _joiner.run(doc, mater_lcs_a, mater_lcs_b)
            if joint is not None:
                _clocker.run(joint)
                # If I don't have all of this here, it'll do all kinds of weird broken reorientations that will never go back to
                # normal unless I go into the brokenly oriented joint and start perturbing settings (e.g., -1 rotation then +1
                # rotation).
                joint.Proxy.updateJCSPlacements(joint)
                joint.Proxy.preSolve(joint, False)
                asm.solve(True)
                doc.recompute()
            else:
                warn(f'Unable to create joint against {mater_lcs_a.Name} and {mater_lcs_b.Name}')
            ret.append(joint)

        doc.commitTransaction()
        return ret
    except Exception:
        doc.abortTransaction()
        raise
    finally:
        doc.recompute()
