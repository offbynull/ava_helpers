import FreeCAD as App
import FreeCADGui as Gui
from dataclasses import dataclass

from logger import error, log


@dataclass
class Selection:
    source: App.DocumentObject
    source_face: tuple[App.DocumentObject, str]
    source_vertex: tuple[App.DocumentObject, str]
    source_edge: tuple [App.DocumentObject, str] | None
    destination: App.DocumentObject
    destination_vertex: tuple[App.DocumentObject, str]


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

    if len(faces) != 1 or len(verts) != 2 or len(edges) not in {0, 1}:
        error('Select exactly one face and two vertices, and optionally one edge.')
        return None

    _, face_parent_obj, face_name = faces[0]
    _, vert1_parent_obj, vert1_name = verts[0]
    _, vert2_parent_obj, vert2_name = verts[1]  # Does not have to be on the same object as everything else
    _, edge_parent_obj, edge_name = edges[0] if edges else (None, None, None)

    src_obj = face_parent_obj
    dst_obj = vert2_parent_obj

    if src_obj != face_parent_obj or src_obj != vert1_parent_obj or (edge_parent_obj is not None and src_obj != edge_parent_obj):
        error('Selected face, first vertex, and edge must be on the same object.')
        return None

    log(f'Selected entities on object 1: {face_name=}, {vert1_name=}, {edge_name=}')
    log(f'Selected entities on object 2: {vert2_name=}')

    return Selection(
        source=src_obj,
        source_face=(src_obj.getSubObject(face_name), face_name),
        source_vertex=(src_obj.getSubObject(vert1_name), vert1_name),
        source_edge=(src_obj.getSubObject(edge_name), edge_name) if edge_name else None,
        destination=dst_obj,
        destination_vertex=(dst_obj.getSubObject(vert2_name), vert2_name)
    )
