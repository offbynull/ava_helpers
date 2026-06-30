# https://chatgpt.com/share/6a42a942-2620-83ea-92cd-bdcfa56aff6f
import math

import FreeCAD as App
import Part

from logger import log, warn


def _gpl(o):
    return o.getGlobalPlacement() if hasattr(o, 'getGlobalPlacement') else o.Placement

def run(
        doc: App.Document,
        mater_lcs: App.DocumentObject,
        obj: App.DocumentObject,
        face_name: str,
        edge_name: str,
):
    face = obj.getSubObject(face_name)
    edge = obj.getSubObject(edge_name)

    # global mater LCS placement/axes
    pl = _gpl(mater_lcs)
    R = pl.Rotation
    x = R * App.Vector(1, 0, 0)
    y = R * App.Vector(0, 1, 0)
    z = R * App.Vector(0, 0, 1)

    # global face
    face_g = face.copy()
    face_g.transformShape(_gpl(obj).toMatrix())

    # global edge
    edge_g = edge.copy()
    edge_g.transformShape(_gpl(obj).toMatrix())

    # use face center as reference
    ref = face_g.CenterOfMass

    # closest point on selected edge to face center
    vertex = Part.Vertex(ref)
    dist, pts, info = edge_g.distToShape(vertex)
    p = pts[0][0]

    # direction from face center toward edge, flattened into face/LCS XY plane
    target = p - ref
    target = target - z * target.dot(z)

    if target.Length < 1e-4:
        warn('Face center projects onto the selected edge; no unique direction.')
        return

    target.normalize()

    # rotate local +Y to target, around local Z
    angle = math.degrees(math.atan2(-x.dot(target), y.dot(target)))

    off = mater_lcs.AttachmentOffset
    off.Rotation = off.Rotation * App.Rotation(App.Vector(0, 0, 1), angle)
    mater_lcs.AttachmentOffset = off

    doc.recompute()
    log(f'Rotated {mater_lcs.Label} by {angle:.6f} deg\n')