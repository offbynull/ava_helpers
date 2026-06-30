import FreeCAD as App

from fixed_joint_mating.mater_lcs_join import mater_lcs_join_helpers
from logger import warn


def run_single(doc: App.Document | None = None):
    if doc is None:
        warn('AvaHelpersWorkbench: no active document.')
        return

    doc.openTransaction('Join mater LCS')
    try:
        mater_lcs_join_helpers.join_selected(doc)
        doc.commitTransaction()
    except Exception:
        doc.abortTransaction()
        raise
    finally:
        doc.recompute()


def run_multi(doc: App.Document | None = None):
    if doc is None:
        warn('AvaHelpersWorkbench: no active document.')
        return

    doc.openTransaction('Join mater LCS')
    try:
        mater_lcs_join_helpers.multi_join_selected(doc)
        doc.commitTransaction()
    except Exception:
        doc.abortTransaction()
        raise
    finally:
        doc.recompute()