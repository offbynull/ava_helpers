import FreeCAD as App
from PySide import QtGui

from fixed_joint_mating.lcs_utils import lcs_creator, lcs_attacher, lcs_attachment_y_facing_edge_orienter, \
    lcs_attachment_y_facing_positive_z_orienter, lcs_detacher
from fixed_joint_mating.lcs_utils.lcs_identifier import MATER_LCS_IDENTIFIER
from fixed_joint_mating.lcs_create.vertex import _selection
from logger import warn


def run(doc: App.Document | None = None):
    if doc is None:
        warn('AvaHelpersWorkbench: no active document.')
        return

    selection = _selection.extract_selection_inputs(doc)
    if selection is None:
        return

    doc.openTransaction('Create mater LCS')
    try:
        src_obj = selection.source
        face_obj, face_name = selection.source_face
        edge_obj, edge_name = (None, None) if not selection.source_edge else selection.source_edge
        for _, vert_name in selection.source_vertices:
            lcs = lcs_creator.run(doc, f'{src_obj.Label}_{MATER_LCS_IDENTIFIER}')
            lcs_attacher.run(doc, lcs, src_obj, face_name, vert_name)
            if edge_name is not None:
                lcs_attachment_y_facing_edge_orienter.run(doc, lcs, src_obj, face_name, edge_name)
            else:
                lcs_attachment_y_facing_positive_z_orienter.run(doc, lcs)
            lcs_detacher.run(doc, lcs)
        doc.commitTransaction()
    except Exception:
        doc.abortTransaction()
        raise
    finally:
        doc.recompute()
