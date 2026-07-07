from dataclasses import dataclass

import FreeCAD as App
import FreeCADGui as Gui

from fixed_joint_mating.lcs_utils import lcs_attacher, lcs_attachment_y_facing_positive_z_orienter, \
    lcs_attachment_y_facing_edge_orienter, lcs_creator, lcs_detacher
from fixed_joint_mating.lcs_utils.lcs_identifier import MATER_LCS_IDENTIFIER
from logger import error, log


@dataclass
class Selection:
    source: App.DocumentObject
    source_face: tuple[App.DocumentObject, str]
    source_vertices: list[tuple[App.DocumentObject, str]]
    source_edge: tuple [App.DocumentObject, str] | None


def extract_selection_inputs(doc: App.Document) -> Selection | None:
    picked = []
    for sx in Gui.Selection.getSelectionEx('', 0):
        for name, sub in zip(sx.SubElementNames, sx.SubObjects):
            st = getattr(sub, 'ShapeType', None)
            if st in ('Face', 'Vertex', 'Edge'):
                picked.append((st, sx.Object, name))
    
    faces = [p for p in picked if p[0] == 'Face']
    verts = [p for p in picked if p[0] == 'Vertex']
    edges = [p for p in picked if p[0] == 'Edge']
    
    if len(faces) != 1 or len(verts) == 0 or len(edges) not in {0, 1}:
        error('Select exactly one face, at least one vertex, and optionally one edge.')
        return None
    
    _, face_obj, face_name = faces[0]
    _, edge_obj, edge_name = edges[0] if edges else (None, None, None)

    for _, vert_obj, vert_name in verts:
        if face_obj != vert_obj:
            error('Selected entities must be on the same object.')
            return None
    if edge_obj is not None and face_obj != edge_obj:
        error('Selected entities must be on the same object.')
        return None

    src_obj = face_obj
    return Selection(
        source=src_obj,
        source_face=(src_obj.getSubObject(face_name), face_name),
        source_vertices=[(src_obj.getSubObject(vert_name), vert_name) for _, _, vert_name in verts],
        source_edge=(src_obj.getSubObject(edge_name), edge_name) if edge_name else None,
    )
