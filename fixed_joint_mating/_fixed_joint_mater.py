import re
import traceback

import FreeCAD as App
from logger import log, warn


# Match LCS labels like "mater", "mater1", "MATER2", etc.
# Only joints whose two referenced LCS objects match this label pattern are modified.
MATE_RE = re.compile(r'(?:^|\s)mater\d*(?:\s|$)', re.I)

# These are the two clocking rotations we settled on:
#
#   ROT_180_Y:
#       Flips the connector frame so the mate orientation lines up the way
#       FreeCAD expects for this fixed-joint setup.
#
#   ROT_180_Z:
#       Spins around the connector's own Z axis. This preserves the Z direction
#       but corrects the Y axis being backwards.
#
# The final clocking rotation is ROT_180_Y.multiply(ROT_180_Z).
ROT_180_Y = App.Rotation(App.Vector(0, 1, 0), 180)
ROT_180_Z = App.Rotation(App.Vector(0, 0, 1), 180)

# Local +Z axis used when comparing connector directions.
Z = App.Vector(0, 0, 1)


def is_fixed_joint(o: 'App.FeaturePython'):
    # FreeCAD document objects are dynamic, so this is intentionally a
    # "duck typing" check instead of checking one exact Python class.
    #
    # A normal Assembly fixed joint should have:
    #   - JointType == "Fixed"
    #   - Reference1 / Reference2: the two selected connector references
    #   - Placement1 / Placement2: FreeCAD's computed joint coordinate systems
    return (
        hasattr(o, 'JointType')
        and str(o.JointType).lower() == 'fixed'
        and hasattr(o, 'Reference1')
        and hasattr(o, 'Reference2')
        and hasattr(o, 'Placement1')
        and hasattr(o, 'Placement2')
    )


def linked_target(o: App.DocumentObject) -> App.GeoFeature:
    # In the Assembly workbench, references usually point at an App::Link,
    # not directly at the real Body/Part/LCS container.
    #
    # LinkedObject is the actual object behind the link.
    return getattr(o, 'LinkedObject')


def child_by_name(parent: App.DocumentObject, name: str):
    # FreeCAD sub-objects are often found by walking OutList.
    # For example, a Body may contain an LCS, and the LCS may contain axes.
    for c in getattr(parent, 'OutList', []):
        if c.Name == name:
            return c
    return None


def resolve_joint_lcs(ref: tuple[App.DocumentObject, list[str]]) -> App.GeoFeature:
    # A joint reference is shaped roughly like:
    #
    #   (<App::Link>, ['LCS.', 'LCS.'])
    #
    # The first item is the linked component.
    # The second item is a list of subpaths inside that component.
    base, subs = ref[0], ref[1]

    # Start at the real object behind the App::Link.
    obj = linked_target(base)

    # For an LCS reference, the first subpath is enough.
    # Example: 'LCS.' -> ['LCS']
    sub = subs[0]
    path = str(sub).strip('.').split('.')

    # Walk down through the object's children until we reach the referenced LCS.
    for name in path:
        obj = child_by_name(obj, name)

    return obj


def is_mate_connector_lcs(o: App.GeoFeature):
    # Only operate on actual Local Coordinate Systems whose labels match MATE_RE.
    #
    # This prevents accidentally clocking arbitrary joints or arbitrary datum
    # objects that happen to be referenced by fixed joints.
    return (
        getattr(o, 'TypeId').endswith('::LocalCoordinateSystem')
        and MATE_RE.search(getattr(o, 'Label', ''))
    )


def update_jcs(j):
    # Placement1 and Placement2 are not the user's original LCS objects.
    # They are FreeCAD's computed Joint Coordinate Systems, derived from:
    #
    #   Reference1 + Offset1 -> Placement1
    #   Reference2 + Offset2 -> Placement2
    #
    # Whenever Offset1/Offset2 changes, ask the joint proxy to recompute these
    # placements before checking directions.
    j.Proxy.updateJCSPlacements(j)


def z_axes_are_correct_after_clocking(j):
    update_jcs(j)

    # UtilsAssembly contains the same helper functions used internally by the
    # Assembly workbench. Importing here keeps this script usable in contexts
    # where the Assembly module is loaded by FreeCAD later.
    import UtilsAssembly

    # Placement1/Placement2 are local to their referenced components.
    # getJcsGlobalPlc converts each JCS into global document coordinates.
    g1 = UtilsAssembly.getJcsGlobalPlc(j.Placement1, j.Reference1)
    g2 = UtilsAssembly.getJcsGlobalPlc(j.Placement2, j.Reference2)

    # Convert each connector's local +Z axis into global coordinates.
    z1 = g1.Rotation.multVec(Z)
    z2 = g2.Rotation.multVec(Z)

    # Important:
    #
    # After the ROT_180_Y + ROT_180_Z clocking offset, the visually correct mate
    # orientation corresponds to a negative dot product here.
    #
    # That feels backwards, but it matches FreeCAD's fixed-joint mating semantics
    # for this setup. Earlier testing showed that using > 0 made the result flip
    # the wrong way.
    return z1.dot(z2) < 0


def flip_to_matching_z_direction(j):
    update_jcs(j)

    # FreeCAD's "Reverse direction" button does not store a boolean property on
    # the joint. It calls flipOnePart(), which moves the unconstrained component.
    #
    # That means flipOnePart() behaves like a toggle: calling it again flips the
    # component back.
    #
    # So we:
    #   1. Check the current direction.
    #   2. Try one flip.
    #   3. Keep it only if the direction is now correct.
    #   4. Otherwise flip back.
    if z_axes_are_correct_after_clocking(j):
        return False

    # Try FreeCAD's own reverse-direction operation.
    j.Proxy.flipOnePart(j)
    update_jcs(j)

    # Keep the trial flip only if it produced the desired Z relationship.
    if z_axes_are_correct_after_clocking(j):
        return True

    # Trial flip was wrong, so toggle back to the original component placement.
    j.Proxy.flipOnePart(j)
    update_jcs(j)

    return False


def clock(docs: list[App.DocumentObject]):
    changed = 0
    skipped = 0

    for j in docs:
        try:
            if not is_fixed_joint(j):
                continue

            # Resolve the two referenced LCS objects so we can filter by label.
            # The joint stores references, not direct LCS objects.
            lcs1 = resolve_joint_lcs(j.Reference1)
            lcs2 = resolve_joint_lcs(j.Reference2)

            log('\nJoint: ' + j.Label)
            log(f'Ref1: {lcs1.Name, lcs1.Label, lcs1.TypeId}')
            log(f'Ref2: {lcs2.Name, lcs2.Label, lcs2.TypeId}')

            # Only clock joints between two recognized mate connector LCSs.
            if not (is_mate_connector_lcs(lcs1) and is_mate_connector_lcs(lcs2)):
                log('Skipped')
                skipped += 1
                continue

            # Offset1 stays identity.
            #
            # Offset2 receives the clocking correction. This is better than
            # writing directly to Placement2 because Placement2 is recomputed
            # by FreeCAD from Reference2 + Offset2.
            j.Offset1 = App.Placement()
            j.Offset2 = App.Placement(App.Vector(), ROT_180_Y.multiply(ROT_180_Z))

            # Clear the computed placements before recomputing. These are not
            # the persistent "design intent"; they are FreeCAD's current JCS
            # results and should be regenerated from the references and offsets.
            j.Placement1 = App.Placement()
            j.Placement2 = App.Placement()

            # Apply FreeCAD's own reverse-direction behavior only if the final
            # global Z directions would otherwise be wrong.
            flipped = flip_to_matching_z_direction(j)

            # Mark the joint dirty so FreeCAD knows it changed.
            j.touch()

            print('CLOCKED' + (' + FLIPPED' if flipped else ''))
            changed += 1

        except Exception:
            warn(f'{j.Label if hasattr(j, "Label") else None}: \n{traceback.format_exc()}')
            skipped += 1

    log(f'\nChanged: {changed} Skipped: {skipped}')


def set_visibility(docs: list[App.DocumentObject], hidden: bool):
    changed = 0
    skipped = 0

    for j in docs:
        try:
            if not is_fixed_joint(j):
                continue

            # Visibility is controlled on the actual LCS view objects, not on
            # the joint references.
            lcs1 = resolve_joint_lcs(j.Reference1)
            lcs2 = resolve_joint_lcs(j.Reference2)

            log('\nJoint: ' + j.Label)
            log(f'Ref1: {lcs1.Name, lcs1.Label, lcs1.TypeId}')
            log(f'Ref2: {lcs2.Name, lcs2.Label, lcs2.TypeId}')

            if not (is_mate_connector_lcs(lcs1) and is_mate_connector_lcs(lcs2)):
                log('Skipped')
                skipped += 1
                continue

            # hidden=True means Visibility=False.
            lcs1.ViewObject.Visibility = not hidden
            lcs2.ViewObject.Visibility = not hidden

            log('HIDDEN' if hidden else 'VISIBLE')
            changed += 1

        except Exception:
            warn(f'{j.Label if hasattr(j, "Label") else None}: \n{traceback.format_exc()}')
            skipped += 1

    log(f'\nChanged: {changed} Skipped: {skipped}')


def toggle_visibility(docs: list[App.DocumentObject]):
    changed = 0
    skipped = 0

    # The same LCS may appear in more than one joint.
    # Track already-seen LCS objects so we do not toggle one LCS twice and end
    # up back where we started.
    seen = set()

    for j in docs:
        try:
            if not is_fixed_joint(j):
                continue

            lcs1 = resolve_joint_lcs(j.Reference1)
            lcs2 = resolve_joint_lcs(j.Reference2)

            log('\nJoint: ' + j.Label)
            log(f'Ref1: {lcs1.Name, lcs1.Label, lcs1.TypeId}')
            log(f'Ref2: {lcs2.Name, lcs2.Label, lcs2.TypeId}')

            if not (is_mate_connector_lcs(lcs1) and is_mate_connector_lcs(lcs2)):
                log('Skipped')
                skipped += 1
                continue

            if lcs1 not in seen:
                lcs1.ViewObject.Visibility = not lcs1.ViewObject.Visibility
                seen.add(lcs1)
                log('Ref 1 VISIBILITY TOGGLED')

            if lcs2 not in seen:
                lcs2.ViewObject.Visibility = not lcs2.ViewObject.Visibility
                seen.add(lcs2)
                log('Ref 2 VISIBILITY TOGGLED')

            changed += 1

        except Exception:
            warn(f'{j.Label if hasattr(j, "Label") else None}: \n{traceback.format_exc()}')
            skipped += 1

    log(f'\nChanged: {changed} Skipped: {skipped}')