import FreeCAD as App

from fixed_joint_mating.mater_lcs import mater_lcs_select_helpers
from fixed_joint_mating.mater_lcs_join import mater_lcs_joiner, mater_lcs_clocker
from logger import error, warn


def join_selected(doc: App.Document) -> App.DocumentObject | None:
    mater_lcses = mater_lcs_select_helpers.pull_selected_objects_that_lead_to_mater_lcs()
    if len(mater_lcses) != 2:
        error('Select exactly two mater LCSes.')
        return None

    joint = mater_lcs_joiner.run(doc, mater_lcses[0], mater_lcses[1])
    if joint is None:
        return None
    mater_lcs_clocker.run(joint)
    return joint


def multi_join_selected(doc: App.Document) -> list[App.DocumentObject] | None:
    mater_lcses = mater_lcs_select_helpers.pull_selected_objects_that_lead_to_mater_lcs()
    if len(mater_lcses) < 2:
        error('Select >= two mater LCSes.')
        return None

    if len(mater_lcses) % 2 != 0:
        error('Number of selected mater LCSes must be divisibly by 2.')
        return None

    ret = []
    mater_lcses_a = mater_lcses[:len(mater_lcses) // 2]
    mater_lcses_b = mater_lcses[len(mater_lcses) // 2:]
    for mater_lcs_a, mater_lcs_b in zip(mater_lcses_a, mater_lcses_b):
        joint = mater_lcs_joiner.run(doc, mater_lcs_a, mater_lcs_b)
        if joint is not None:
            mater_lcs_clocker.run(joint)
        else:
            warn(f'Unable to create joint against {mater_lcs_a.Name} and {mater_lcs_b.Name}')
        ret.append(joint)
    return ret
