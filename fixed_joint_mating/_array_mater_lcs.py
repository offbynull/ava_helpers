# https://chatgpt.com/share/6a42b763-d3c4-83ea-a8ab-978288c3d377
import math
from dataclasses import dataclass
from enum import Enum

import FreeCAD as App
import FreeCADGui as Gui

from fixed_joint_mating import _mater_lcs_creator, _mater_lcs_attacher, \
    _mater_lcs_attachment_y_facing_positive_z_orienter, _mater_lcs_attachment_y_facing_edge_orienter
from logger import error, log


@dataclass
class Selection:
    source: App.DocumentObject
    source_face: tuple[App.DocumentObject, str]
    source_vertex: tuple[App.DocumentObject, str]
    source_edge: tuple [App.DocumentObject, str] | None
    destination: App.DocumentObject
    destination_vertex: tuple[App.DocumentObject, str]


def extract_selection(doc: App.Document) -> Selection | None:
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


_LCS_NAME = 'MaterLCS'


class OffsetApplicationCoordinateSystem(Enum):
    GLOBAL = 'GLOBAL'
    LCS = 'LCS'


@dataclass
class Offset:
    x: float
    y: float
    z: float
    coordinate_system_application: OffsetApplicationCoordinateSystem


def execute(
        doc: App.Document,
        selection: Selection,
        name_prefix: str,
        spacing: float,
        offset: Offset
) -> None:
    src = selection.source
    src_vertex_obj, src_vertex_name = selection.source_vertex
    _, src_face_name = selection.source_face
    _, src_edge_name = selection.source_edge if selection.source_edge else (None, None)

    dst = selection.destination
    dst_vertex_obj, _ = selection.destination_vertex

    p0 = App.Vector(src_vertex_obj.Point)  # Don't do this - getSubObject() defaults transform=True: src.getGlobalPlacement().multVec(src_vertex_obj.Point)
    p1 = App.Vector(dst_vertex_obj.Point)  # Don't do this - getSubObject() defaults transform=True: dst.getGlobalPlacement().multVec(dst_vertex_obj.Point)
    vec = p1 - p0
    length = vec.Length

    if length <= 1e-4:
        error('Vertices are coincident.')
        return

    direction = App.Vector(vec)
    direction.normalize()

    if spacing == 0:
        error('Spacing cannot be zero.')
        return
    if spacing < 0:
        error('Spacing cannot be negative.')
        return
        
    count = int(math.floor(length / spacing)) + 1

    for i in range(count):
        mater_lcs = _mater_lcs_creator.run(
            doc=doc,
            name=f'{name_prefix}_{_LCS_NAME}_{i:03d}'
        )
        _mater_lcs_attacher.run(doc, mater_lcs, src, src_face_name, src_vertex_name)
        if src_edge_name is not None:
            _mater_lcs_attachment_y_facing_edge_orienter.run(doc, mater_lcs, src, src_face_name, src_edge_name)
        else:
            _mater_lcs_attachment_y_facing_positive_z_orienter.run(doc, mater_lcs)

        doc.recompute()  # important: make attachment placement valid

        target_global = p0 + direction * (i * spacing)
        if offset.coordinate_system_application == OffsetApplicationCoordinateSystem.GLOBAL:
            target_global.x += offset.x
            target_global.y += offset.y
            target_global.z += offset.z

        current_offset = App.Placement(mater_lcs.AttachmentOffset)
        anchor_global = mater_lcs.getGlobalPlacement().multiply(current_offset.inverse())
        local_point = anchor_global.inverse().multVec(target_global)
        if offset.coordinate_system_application == OffsetApplicationCoordinateSystem.LCS:
            local_point.x += offset.x
            local_point.y += offset.y
            local_point.z += offset.z

        new_offset = App.Placement(current_offset)
        new_offset.Base = local_point
        mater_lcs.AttachmentOffset = new_offset

    doc.recompute()
    log(f'Created {count} independent LCS objects.')


# def run(doc: App.Document, spacing: float = 2.0) -> None:
#     selection = extract_selection(doc)
#     if selection is not None:
#         execute(doc, selection, spacing)