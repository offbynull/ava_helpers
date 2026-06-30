# https://chatgpt.com/share/6a42a942-2620-83ea-92cd-bdcfa56aff6f
import math

import FreeCAD as App

from logger import log, warn


def _gpl(o):
    return o.getGlobalPlacement() if hasattr(o, 'getGlobalPlacement') else o.Placement

def _support_obj(o):
    s = getattr(o, 'Support', None)
    if s:
        first = s[0]
        return first[0] if isinstance(first, tuple) else first
    return None



def run(
        doc: App.Document,
        mater_lcs: App.DocumentObject,
        target: App.Vector | None = None
):
    parent = _support_obj(mater_lcs)
    Rlcs_g = _gpl(mater_lcs).Rotation
    Rpar_g = _gpl(parent).Rotation if parent else App.Rotation()
    to_parent = Rpar_g.inverted()
    
    x = to_parent * (Rlcs_g * App.Vector(1,0,0))
    y = to_parent * (Rlcs_g * App.Vector(0,1,0))
    z = to_parent * (Rlcs_g * App.Vector(0,0,1))

    if target is None:
        target = App.Vector(0,0,1)       # +Z in parent coordinates
    tp = target - z * target.dot(z)  # projection into LCS XY plane
    
    if tp.Length < 1e-4:
        warn('Cannot reorient Y by rotating about LCS Z (projection failed).')
        return
    
    tp = tp * (1.0 / tp.Length)
    
    angle = math.degrees(math.atan2(-x.dot(tp), y.dot(tp)))
    
    off = mater_lcs.AttachmentOffset
    off.Rotation = off.Rotation * App.Rotation(App.Vector(0,0,1), angle)
    mater_lcs.AttachmentOffset = off
    
    doc.recompute()
    
    log(f'Rotated {mater_lcs.Label} about local Z by {angle:.6f} deg')