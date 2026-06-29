import FreeCAD as App
import FreeCADGui as Gui

from fixed_joint_mating import _mater_lcs_creator, _mater_lcs_attacher, \
    _mater_lcs_attachment_y_facing_positive_z_orienter, _mater_lcs_attachment_y_facing_edge_orienter
from logger import error, log


def run(doc: App.Document) -> None:
    picked = []
    for sx in Gui.Selection.getSelectionEx('', 0):
        for name, sub in zip(sx.SubElementNames, sx.SubObjects):
            st = getattr(sub, 'ShapeType', None)
            if st in ('Face', 'Vertex', 'Edge'):
                picked.append((st, sx.Object, name))
    
    faces = [p for p in picked if p[0] == 'Face']
    verts = [p for p in picked if p[0] == 'Vertex']
    edges = [p for p in picked if p[0] == 'Edge']
    
    if len(faces) != 1 or len(verts) != 1 or len(edges) not in {0, 1}:
        error('Select exactly one face and one vertex, and optionally one edge.')
        return
    
    _, face_obj, face_name = faces[0]
    _, vert_obj, vert_name = verts[0]
    _, edge_obj, edge_name = edges[0] if edges else (None, None, None)

    if face_obj != vert_obj or (edge_obj is not None and face_obj != edge_obj):
        error('Selected entities must be on the same object.')
        return

    log(f'Selected entities: {face_name=}, {vert_name=}, {edge_name=}')

    mater_lcs = _mater_lcs_creator.run(doc)
    _mater_lcs_attacher.run(doc, mater_lcs, face_obj, face_name, vert_name)
    if edge_name is not None:
        log('PLACING TOWARDS EDGE')
        _mater_lcs_attachment_y_facing_edge_orienter.run(doc, mater_lcs, face_obj, face_name, edge_name)
    else:
        _mater_lcs_attachment_y_facing_positive_z_orienter.run(doc, mater_lcs)