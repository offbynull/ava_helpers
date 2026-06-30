# https://chatgpt.com/share/6a42b763-d3c4-83ea-a8ab-978288c3d377

import FreeCAD as App

from fixed_joint_mating.mater_lcs import mater_lcs_attacher, mater_lcs_attachment_y_facing_positive_z_orienter, \
    mater_lcs_attachment_y_facing_edge_orienter
from fixed_joint_mating.mater_lcs.mater_lcs_array_parameters import Offset, OffsetApplicationCoordinateSystem
from logger import error


def _vector_pair_to_points_direction_length(
    src_vertex_obj: App.DocumentObject,
    dst_vertex_obj: App.DocumentObject
) -> tuple[App.Vector, App.Vector, App.Vector, float] | None:
    p0 = App.Vector(src_vertex_obj.Point)  # Don't do this - getSubObject() defaults transform=True: src.getGlobalPlacement().multVec(src_vertex_obj.Point)
    p1 = App.Vector(dst_vertex_obj.Point)  # Don't do this - getSubObject() defaults transform=True: dst.getGlobalPlacement().multVec(dst_vertex_obj.Point)
    vec = p1 - p0
    length = vec.Length

    if length <= 1e-4:
        error('Vertices are coincident.')
        return None

    direction = App.Vector(vec)
    direction.normalize()

    return p0, p1, direction, length


def _attach_mater_and_orient(
        doc: App.Document,
        p0: App.Vector,
        direction: App.Vector,
        mater_lcs: App.DocumentObject,
        mater_lcs_instance: int,
        offset: Offset,
        spacing: float,
        src: App.DocumentObject,
        src_edge_name: str,
        src_face_name: str,
        src_vertex_name: str
) -> None:
    mater_lcs_attacher.run(doc, mater_lcs, src, src_face_name, src_vertex_name)
    if src_edge_name is not None:
        mater_lcs_attachment_y_facing_edge_orienter.run(doc, mater_lcs, src, src_face_name, src_edge_name)
    else:
        mater_lcs_attachment_y_facing_positive_z_orienter.run(doc, mater_lcs)

    doc.recompute()  # important: make attachment placement valid

    target_global = p0 + direction * (mater_lcs_instance * spacing)
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
