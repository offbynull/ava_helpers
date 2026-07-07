import re

import FreeCAD as App
from PySide import QtGui

from fixed_joint_mating.lcs_utils import lcs_selection_helpers
from fixed_joint_mating.lcs_create.array._array_parameter_storage import read_inputs_from_varset
from fixed_joint_mating.lcs_create.array._utils import _attach_mater_and_orient, \
    _vector_pair_to_points_direction_length
from fixed_joint_mating.lcs_utils.lcs_identifier import MATER_LCS_IDENTIFIER
from logger import log, warn


def _update(
        doc: App.Document,
        maters: list[App.DocumentObject],
) -> None:
    for mater_lcs in maters:
        m = re.search(r'(.*?)_' + re.escape(MATER_LCS_IDENTIFIER) + r'_(\d{3})', mater_lcs.Name)
        if not m:
            warn(f'Skipping {mater_lcs.Name} - unrecognized name.')
            continue
        name_prefix = m.group(1)
        mater_lcs_instance = int(m.group(2))

        selection, name_prefix, spacing, offset = read_inputs_from_varset(doc, f'{name_prefix}_{MATER_LCS_IDENTIFIER}')

        src = selection.source
        src_vertex_obj, src_vertex_name = selection.source_vertex
        src_face_obj, src_face_name = selection.source_face
        src_edge_obj, src_edge_name = selection.source_edge
        dst = selection.destination
        dst_vertex_obj, dst_vertex_name = selection.destination_vertex

        ret = _vector_pair_to_points_direction_length(src_vertex_obj, dst_vertex_obj)
        if ret is None:
            warn(f'Skipping {mater_lcs.Name} - Unable to extract point and direction.')
            continue
        p0, p1, direction, length = ret

        if spacing == 0:
            warn(f'Skipping {mater_lcs.Name} - Spacing cannot be zero.')
            continue
        if spacing < 0:
            warn(f'Skipping {mater_lcs.Name} - Spacing cannot be negative.')
            continue

        _attach_mater_and_orient(
            doc,
            p0,
            direction,
            mater_lcs,
            mater_lcs_instance,
            offset,
            spacing,
            src,
            src_edge_name,
            src_face_name,
            src_vertex_name
        )
        log(f'Repaired {mater_lcs.Name}.')


def run(doc: App.Document | None = None):
    if doc is None:
        warn('AvaHelpersWorkbench: no active document.')
        return

    mater_lcses = lcs_selection_helpers.pull_selected_objects_that_lead_to_mater_lcs()
    mater_lcses = [l.obj for l in mater_lcses]

    doc.openTransaction('Update mater LCS array')
    try:
        _update(doc, mater_lcses)
        doc.commitTransaction()
    except Exception:
        doc.abortTransaction()
        raise
    finally:
        doc.recompute()