# https://chatgpt.com/share/6a394267-8320-83ea-8eeb-6978b4bc0678
import math
from typing import Any, cast

import FreeCAD as App
import FreeCADGui as Gui

from logger import log, warn

TOL = 1e-7

Z_AXIS = App.Vector(0, 0, 1)
POS_Z = App.Vector(0, 0, 1)
NEG_Z = App.Vector(0, 0, -1)


def fail(msg: str):
    raise Exception(f'Forward Flusher: {msg}')


def unit(v: App.Vector, name) -> App.Vector:
    v = App.Vector(v.x, v.y, v.z)
    if v.Length < TOL:
        fail(f'{name} is too small.')
    v.normalize()
    return v


def scale(v: App.Vector, s: float) -> App.Vector:
    return App.Vector(v.x * s, v.y * s, v.z * s)


def project_out(v: App.Vector, n: App.Vector) -> App.Vector:
    return v - scale(n, v.dot(n))


def is_same_edge(a: Any, b: Any) -> bool:
    for method in ('isSame', 'isEqual', 'isPartner'):
        try:
            if getattr(a, method)(b):
                return True
        except Exception:
            pass

    av = [x.Point for x in a.Vertexes]
    bv = [x.Point for x in b.Vertexes]

    if len(av) == 2 and len(bv) == 2:
        return (
            av[0].distanceToPoint(bv[0]) < TOL and
            av[1].distanceToPoint(bv[1]) < TOL
        ) or (
            av[0].distanceToPoint(bv[1]) < TOL and
            av[1].distanceToPoint(bv[0]) < TOL
        )

    return False


def get_selection() -> tuple[App.DocumentObject, str, str]:
    face_obj: App.DocumentObject | None = None
    edge_obj: App.DocumentObject | None = None
    face_name: str | None = None
    edge_name: str | None = None

    for sx in Gui.Selection.getSelectionEx():
        for name, sub in zip(sx.SubElementNames, sx.SubObjects):
            st = getattr(sub, 'ShapeType', '')

            if st == 'Face':
                if face_name:
                    fail('Select exactly one face.')
                face_obj = sx.Object
                face_name = name

            elif st == 'Edge':
                if edge_name:
                    fail('Select exactly one edge.')
                edge_obj = sx.Object
                edge_name = name

    if not face_name or not edge_name:
        fail('Select one planar face and one straight edge.')

    if face_obj != edge_obj:
        fail('Face and edge must be on the same selected object/feature.')

    ret = face_obj, face_name, edge_name
    return cast(tuple[App.DocumentObject, str, str], ret)


def get_placement_object(sel_obj: App.DocumentObject) -> App.DocumentObject:
    # If a Part Design feature was selected, move its parent Body.
    if 'PartDesign::Body' in getattr(sel_obj, 'TypeId', ''):
        return sel_obj

    try:
        parent = sel_obj.getParentGeoFeatureGroup()
        if parent and 'PartDesign::Body' in getattr(parent, 'TypeId', ''):
            return cast(App.DocumentObject, parent)
    except Exception:
        pass

    for parent in getattr(sel_obj, 'InListRecursive', []):
        if 'PartDesign::Body' in getattr(parent, 'TypeId', ''):
            return parent

    return sel_obj


def rotation_matrix(rot: App.Rotation) -> App.Matrix:
    return App.Placement(App.Vector(0, 0, 0), rot).toMatrix()


def rotated_shape(shape: Any, rot: App.Rotation) -> Any:
    # Rotate a copy only; do not touch the actual object.
    s = shape.copy()
    s.transformShape(rotation_matrix(rot), True)
    return s


def combine_rotations(first_rot: App.Rotation, second_rot: App.Rotation):
    # Return a rotation that applies first_rot, then second_rot.
    candidates = [
        second_rot.multiply(first_rot),
        first_rot.multiply(second_rot),
    ]

    # Caller will validate which one behaves correctly.
    return candidates


def choose_face_seating_rotation(move_shape: Any, face: Any, face_normal: App.Vector) -> tuple[float, float, App.Rotation]:
    candidates = []

    # A face can be parallel to XY two ways:
    #   normal -> +Z
    #   normal -> -Z
    #
    # Both make the face flat.
    # We keep the one where the selected face becomes the object's lowest face.
    for target_normal in (POS_Z, NEG_Z):
        rot = App.Rotation(face_normal, target_normal)
        rot_m = rotation_matrix(rot)
        test_shape = rotated_shape(move_shape, rot)

        object_lowest_z = test_shape.BoundBox.ZMin

        # Rotate all selected-face vertices.
        face_zs = [
            rot_m.multVec(vertex.Point).z
            for vertex in face.Vertexes
        ]

        # If every face vertex is at the object's lowest Z,
        # then this selected face is seated on the XY side.
        face_flat_error = max(face_zs) - min(face_zs)
        face_bottom_error = max(abs(z - object_lowest_z) for z in face_zs)

        candidates.append((
            face_bottom_error,
            face_flat_error,
            rot,
        ))

    best = min(candidates, key=lambda c: (c[0], c[1]))
    return best


def choose_edge_forward_rotation(base_rot:App.Rotation, face: Any, edge: Any, edge_dir: App.Vector) -> tuple[float, float, App.Rotation]:
    candidates = []

    # After face seating, get the edge direction in world XY.
    seated_edge_dir = unit(base_rot.multVec(edge_dir), 'Seated edge direction')
    seated_edge_xy = unit(
        App.Vector(seated_edge_dir.x, seated_edge_dir.y, 0),
        'Seated edge XY direction'
    )

    # Find the Z rotation that makes the edge parallel to +X.
    angle_to_x = math.degrees(math.atan2(
        -seated_edge_xy.y,
        seated_edge_xy.x
    ))

    # There are two valid X-parallel choices:
    #   angle_to_x       -> edge parallel to +X
    #   angle_to_x + 180 -> edge parallel to -X
    #
    # Both are parallel to X.
    # We keep the one where the selected edge becomes the -Y edge of the face.
    for extra in (0, 180):
        z_rot = App.Rotation(Z_AXIS, angle_to_x + extra)

        for final_rot in combine_rotations(base_rot, z_rot):
            final_m = rotation_matrix(final_rot)

            # Rotate all selected-face vertices with this final rotation.
            face_points = [
                final_m.multVec(vertex.Point)
                for vertex in face.Vertexes
            ]

            lowest_face_y = min(p.y for p in face_points)

            # Rotate selected edge endpoints with the same final rotation.
            p1 = final_m.multVec(edge.valueAt(edge.FirstParameter))
            p2 = final_m.multVec(edge.valueAt(edge.LastParameter))

            # The selected edge is the -Y edge if both selected-edge endpoint
            # Y values are <= every other face vertex Y.
            selected_edge_highest_y = max(p1.y, p2.y)
            edge_front_error = max(0.0, selected_edge_highest_y - lowest_face_y)

            # Confirm the selected edge is actually X-parallel.
            final_edge_dir = unit(final_rot.multVec(edge_dir), 'Final edge direction')
            edge_parallel_x_error = abs(final_edge_dir.y) + abs(final_edge_dir.z)

            candidates.append((
                edge_front_error,
                edge_parallel_x_error,
                final_rot,
            ))

    best = min(candidates, key=lambda c: (c[0], c[1]))
    return best


def run(doc: App.Document | None = None) -> None:
    sel_obj, face_name, edge_name = get_selection()
    move_obj = get_placement_object(sel_obj)

    # Reset placement so repeated runs do not compound previous placement data.
    move_obj.Placement = App.Placement(
        App.Vector(0, 0, 0),
        App.Rotation(Z_AXIS, 0)
    )
    App.ActiveDocument.recompute()

    face = sel_obj.Shape.getElement(face_name)
    edge = sel_obj.Shape.getElement(edge_name)

    if 'Plane' not in face.Surface.TypeId:
        fail('Selected face must be planar.')

    if 'Line' not in edge.Curve.TypeId:
        fail('Selected edge must be straight.')

    if not any(is_same_edge(edge, e) for e in face.Edges):
        fail('Selected edge must belong to the selected face.')

    # Get the selected face normal.
    u, v = face.Surface.parameter(face.CenterOfMass)
    face_normal = unit(face.normalAt(u, v), 'Face normal')

    # Get the selected edge direction.
    edge_p1 = edge.valueAt(edge.FirstParameter)
    edge_p2 = edge.valueAt(edge.LastParameter)
    edge_dir = unit(edge_p2 - edge_p1, 'Edge direction')

    # Force edge direction to lie in the face plane.
    edge_dir = unit(project_out(edge_dir, face_normal), 'Projected edge direction')

    # PHASE 1:
    # Rotate so the selected face sits flat on XY as the object's bottom face.
    face_bottom_err, face_flat_err, face_rot = choose_face_seating_rotation(
        move_obj.Shape,
        face,
        face_normal
    )

    if face_bottom_err > 1e-5:
        warn('Warning: selected face may not be the lowest face.\n')

    if face_flat_err > 1e-5:
        warn('Warning: selected face may not be flat on XY.\n')

    # PHASE 2:
    # Starting from the seated face rotation, spin around Z so the selected edge
    # is X-parallel and is the -Y edge of the selected face.
    edge_front_err, edge_parallel_err, final_rot = choose_edge_forward_rotation(
        face_rot,
        face,
        edge,
        edge_dir
    )

    if edge_parallel_err > 1e-5:
        warn('Warning: selected edge may not be parallel to X.\n')

    if edge_front_err > 1e-5:
        warn('Warning: selected edge may not be the -Y edge of the face.\n')

    # After final rotation, move object so its lowest point is exactly Z=0.
    final_shape = rotated_shape(move_obj.Shape, final_rot)
    object_lowest_z = final_shape.BoundBox.ZMin

    translation = App.Vector(0, 0, -object_lowest_z)

    move_obj.Placement = App.Placement(translation, final_rot)

    App.ActiveDocument.recompute()

    log('Done: face is seated on XY; selected edge is X-parallel on the -Y side.')