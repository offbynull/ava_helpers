import FreeCAD as App
from screw.geometries.cone_frustum import ConeFrustum
from screw.geometries.cylinder import Cylinder
from screw.thread_profile_extents import ThreadProfileExtents


def minor_shape_to_major_shape(
        minor_shape: ConeFrustum | Cylinder,
        thread_profile_extents: ThreadProfileExtents,
):
    offset_to_bottom_radius, distance_from_bottom = thread_profile_extents.point_with_max_x
    if isinstance(minor_shape, ConeFrustum):
        # Imagine that the thread where wrapping around the minor cone. The thread is sketched below the X axis. It must
        # perform 1 full revolution for the part of the profile below the X axis to appear and bond to the minor cone.
        # As that revolution is performed, the helix also expands out to match the cone frustum's contour.
        #
        # Shift the cone frustum up such that its bottom is moved to the thickest part of that first revolution.
        #
        #     ___________
        #     \         /
        #      \       /
        #       \     /
        #        \___/
        #             ▶       Imagine moving this thread up the cone for up to 1 full revolution, stopping at the
        #                     thickest part. Update the cone's bottom to be where that thickest part is.
        #
        # This same process applies even if the cone were flipped (thin-top thick-bottom vs thick-top thin-bottom).
        shifted_minor_shape = minor_shape.shift(-distance_from_bottom)
        # Pull out the new radius of the bottom, then tack on the width of the thickest part of the thread.
        shifted_major_bottom_radius = shifted_minor_shape.bottom_radius + offset_to_bottom_radius
        # The difference between this new radius and the original minor shape's radius is offset between minor cone and
        # the major cone.
        radius_offset = shifted_major_bottom_radius - minor_shape.bottom_radius
        major_shape = minor_shape.widen(radius_offset)
    else:
        major_shape = minor_shape.widen(offset_to_bottom_radius)
    return major_shape


def offset_attachment_using_parent_coordinates(
        parent: App.DocumentObject,
        child: App.DocumentObject,
        offset: App.Vector
):
    parent_rotation = parent.getGlobalPlacement().Rotation
    child_rotation = child.getGlobalPlacement().Rotation
    # parent vector -> world -> attachment-local
    v_offset = child_rotation.inverted().multVec(parent_rotation.multVec(offset))
    child_offset = child.AttachmentOffset
    child_offset.Base = child_offset.Base + v_offset
    child.AttachmentOffset = child_offset


def offset_attachment_using_parent_coordinates(
        parent: App.DocumentObject,
        child: App.DocumentObject,
        offset: App.Vector
):
    parent_rotation = parent.getGlobalPlacement().Rotation
    child_rotation = child.getGlobalPlacement().Rotation
    # parent vector -> world -> attachment-local
    v_offset = child_rotation.inverted().multVec(parent_rotation.multVec(offset))
    child_offset = child.AttachmentOffset
    child_offset.Base = child_offset.Base + v_offset
    child.AttachmentOffset = child_offset
