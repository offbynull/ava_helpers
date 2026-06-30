import FreeCAD as App

from logger import log

# Set this default however you prefer.
#
# True:
#   The visible/original mate LCS Z axes should point the same way.
#
# False:
#   The visible/original mate LCS Z axes should point opposite ways.
#
# In both cases, the visible/original mate LCS Y axes should point the same way.
SAME_Z_DIR = False

# Clocking rotations.
#
# ROT_180_Y:
#   Flips X and Z, but keeps Y the same.
#   This is the useful correction when we want:
#
#       Z opposite
#       Y same
#
# ROT_180_Z:
#   Flips X and Y, but keeps Z the same.
#   This was useful in the earlier experiment, but it is NOT used for the final
#   same/opposite-Z mode here because it makes Y point the wrong way.
ROT_180_Y = App.Rotation(App.Vector(0, 1, 0), 180)
ROT_180_Z = App.Rotation(App.Vector(0, 0, 1), 180)

# Local +Z axis used when comparing connector directions.
Z = App.Vector(0, 0, 1)


def clocking_rotation(same_z_dir: bool):
    # This returns the Offset2 rotation we want FreeCAD to use when computing
    # Placement2 from Reference2.
    #
    # FreeCAD tries to align the two computed Joint Coordinate Systems.
    # Offset2 lets us define how the visible/original second LCS should relate
    # to that computed JCS.
    #
    # same_z_dir=True:
    #   Use no extra rotation. If the computed JCS frames align, the visible LCS
    #   frames also have:
    #
    #       Z same
    #       Y same
    #
    # same_z_dir=False:
    #   Use 180 degrees around Y. This keeps Y unchanged but reverses Z, giving:
    #
    #       Z opposite
    #       Y same
    if same_z_dir:
        return App.Rotation()

    return ROT_180_Y


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

    # Convert each computed JCS's local +Z axis into global coordinates.
    z1 = g1.Rotation.multVec(Z)
    z2 = g2.Rotation.multVec(Z)

    # With the final clocking strategy, the computed JCS frames should always
    # end up with their Z axes pointing the same way.
    #
    # The visible/original LCS same-vs-opposite choice is handled by Offset2:
    #
    #   same_z_dir=True  -> Offset2 identity     -> visible Z same,     visible Y same
    #   same_z_dir=False -> Offset2 ROT_180_Y    -> visible Z opposite, visible Y same
    #
    # So the check here no longer branches on same_z_dir.
    return z1.dot(z2) > 0


def flip_to_matching_z_direction(j):
    update_jcs(j)

    # FreeCAD's "Reverse direction" button does not store a boolean property on
    # the joint. It calls flipOnePart(), which moves the unconstrained component.
    #
    # That means flipOnePart() behaves like a toggle: calling it again flips the
    # component back.
    #
    # So we:
    #   1. Check the current computed JCS direction.
    #   2. Try one flip.
    #   3. Keep it only if the computed JCS direction is now correct.
    #   4. Otherwise flip back.
    if z_axes_are_correct_after_clocking(j):
        return False

    # Try FreeCAD's own reverse-direction operation.
    j.Proxy.flipOnePart(j)
    update_jcs(j)

    # Keep the trial flip only if it produced the desired JCS Z relationship.
    if z_axes_are_correct_after_clocking(j):
        return True

    # Trial flip was wrong, so toggle back to the original component placement.
    j.Proxy.flipOnePart(j)
    update_jcs(j)

    return False


# clock
def run(j: App.DocumentObject, same_z_dir: bool = SAME_Z_DIR):
    if not is_fixed_joint(j):
        return

    # Resolve the two referenced LCS objects so we can filter by label.
    # The joint stores references, not direct LCS objects.
    lcs1 = resolve_joint_lcs(j.Reference1)
    lcs2 = resolve_joint_lcs(j.Reference2)

    log('\nJoint: ' + j.Label)
    log(f'Ref1: {lcs1.Name, lcs1.Label, lcs1.TypeId}')
    log(f'Ref2: {lcs2.Name, lcs2.Label, lcs2.TypeId}')

    # Offset1 stays identity.
    #
    # Offset2 receives the clocking correction. This is better than
    # writing directly to Placement2 because Placement2 is recomputed
    # by FreeCAD from Reference2 + Offset2.
    #
    # The important final rule is:
    #
    #   same_z_dir=True:
    #       Offset2 = identity
    #       visible/original LCS Z same
    #       visible/original LCS Y same
    #
    #   same_z_dir=False:
    #       Offset2 = ROT_180_Y
    #       visible/original LCS Z opposite
    #       visible/original LCS Y same
    #
    # Do not always apply ROT_180_Z here. ROT_180_Z flips Y, which is
    # exactly what caused the "Z is opposite, but Y is also opposite"
    # problem.
    j.Offset1 = App.Placement()
    j.Offset2 = App.Placement(App.Vector(), clocking_rotation(same_z_dir))

    # Clear the computed placements before recomputing. These are not
    # the persistent "design intent"; they are FreeCAD's current JCS
    # results and should be regenerated from the references and offsets.
    j.Placement1 = App.Placement()
    j.Placement2 = App.Placement()

    # Apply FreeCAD's own reverse-direction behavior only if the final
    # computed JCS Z directions would otherwise be wrong.
    #
    # Because flipOnePart() is a toggle, flip_to_matching_z_direction()
    # tries it, checks the resulting global JCS directions, and toggles
    # back if that trial was not the requested state.
    flipped = flip_to_matching_z_direction(j)

    # Mark the joint dirty so FreeCAD knows it changed.
    j.touch()

    log(
        'CLOCKED'
        + (' + FLIPPED' if flipped else '')
        + (' + SAME_Z' if same_z_dir else ' + OPPOSITE_Z')
        + ' + SAME_Y'
    )
