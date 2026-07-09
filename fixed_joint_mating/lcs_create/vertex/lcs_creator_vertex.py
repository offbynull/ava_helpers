import FreeCAD as App
from PySide import QtGui

from fixed_joint_mating.lcs_utils import lcs_creator, lcs_attacher, lcs_attachment_y_facing_edge_orienter, \
    lcs_attachment_y_facing_positive_z_orienter, lcs_detacher
from fixed_joint_mating.lcs_utils.lcs_identifier import MATER_LCS_IDENTIFIER
from logger import warn, error
from utils.selection import extract_selection_inputs, SubelementType


def run(doc: App.Document | None = None):
    if doc is None:
        warn('AvaHelpersWorkbench: no active document.')
        return

    selection = extract_selection_inputs(doc)
    faces = [p for p in selection if p.type == SubelementType.FACE]
    verts = [p for p in selection if p.type == SubelementType.VERTEX]
    edges = [p for p in selection if p.type == SubelementType.EDGE]
    if len(faces) != 1 or len(verts) == 0 or len(edges) not in {0, 1}:
        error('Select exactly one face and one vertex, and optionally one edge.')
        return
    for vert in verts:
        if faces[0].unresolved.parent_object != vert.unresolved.parent_object:
            error('Selected entities must be on the same object.')
            return
    if len(edges) != 0 and faces[0].unresolved.parent_object != edges[0].unresolved.parent_object:
        error('Selected entities must be on the same object.')
        return

    doc.openTransaction('Create mater LCS')
    try:
        parent_obj = faces[0].unresolved.parent_object
        face_name = faces[0].unresolved.subelement_name
        edge_name = None if not edges else edges[0].unresolved.subelement_name
        for vert in verts:
            vert_name = vert.unresolved.subelement_name
            lcs = lcs_creator.run(doc, f'{parent_obj.Label}_{MATER_LCS_IDENTIFIER}')
            lcs_attacher.run(doc, lcs, parent_obj, face_name, vert_name)
            if edge_name is not None:
                lcs_attachment_y_facing_edge_orienter.run(doc, lcs, parent_obj, face_name, edge_name)
            else:
                lcs_attachment_y_facing_positive_z_orienter.run(doc, lcs)
            lcs_detacher.run(doc, lcs)
        doc.commitTransaction()
    except Exception:
        doc.abortTransaction()
        raise
    finally:
        doc.recompute()
