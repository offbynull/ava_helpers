# https://chatgpt.com/share/6a42b763-d3c4-83ea-a8ab-978288c3d377
import math
import re

import FreeCAD as App
import FreeCADGui as Gui

from fixed_joint_mating.mater_lcs import mater_lcs_creator
from fixed_joint_mating.mater_lcs.mater_lcs_identifier import MATER_LCS_IDENTIFIER
from fixed_joint_mating.mater_lcs._array_utils import _attach_mater_and_orient, \
    _vector_pair_to_points_direction_length
from fixed_joint_mating.mater_lcs.mater_lcs_array_parameters import Selection, Offset
from fixed_joint_mating.mater_lcs._array_parameter_storage import write_inputs_to_varset, read_inputs_from_varset
from logger import error, log, warn


def create(
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

    write_inputs_to_varset(doc, f'{name_prefix}_{MATER_LCS_IDENTIFIER}', selection, spacing, offset)

    ret = _vector_pair_to_points_direction_length(src_vertex_obj, dst_vertex_obj)
    if ret is None:
        error('Unable to extract point and direction.')
        return
    p0, p1, direction, length = ret

    if spacing == 0:
        error('Spacing cannot be zero.')
        return
    if spacing < 0:
        error('Spacing cannot be negative.')
        return
        
    count = int(math.floor(length / spacing)) + 1

    for mater_lcs_instance in range(count):
        mater_lcs = mater_lcs_creator.run(
            doc=doc,
            name=f'{name_prefix}_{MATER_LCS_IDENTIFIER}_{mater_lcs_instance:03d}'
        )
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

    doc.recompute()
    log(f'Created {count} maters.')


def update(
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
