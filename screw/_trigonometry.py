import math

import FreeCAD as App


def cone_frustum_to_angle(radius1: App.Units.Quantity, radius2: App.Units.Quantity, radius_distance: App.Units.Quantity):
    # This is a cone frustrum: There's a height and two radiuses. Those heights and two radiuses form a trangle - use it
    # to get the angle of the cone, from the axis.
    if radius1 == radius2:
        return 0 * App.Units.Degree
    raw_radius_small, raw_radius_large = sorted([radius1.Value, radius2.Value])
    raw_radius_distance = radius_distance.Value
    raw_angle = math.degrees(
        math.atan((raw_radius_large - raw_radius_small) / raw_radius_distance)
    )
    if radius1.Value != raw_radius_small:
        raw_angle = -raw_angle
    angle = raw_angle * App.Units.Degree
    return angle


def cone_height_at_radius(angle: App.Units.Quantity, target_radius: App.Units.Quantity):
    raw_angle = angle.Value
    flipped = False
    if raw_angle < 0:
        raw_angle = -raw_angle
        flipped = True
    raw_opposite = target_radius.Value
    raw_adjacent = raw_opposite / math.tan(math.radians(raw_angle))
    if flipped:
        raw_adjacent = -raw_adjacent
    adjacent = raw_adjacent * App.Units.MilliMetre
    return adjacent


def cone_radius_at_height(angle: App.Units.Quantity, target_height: App.Units.Quantity):
    raw_angle = angle.Value
    flipped = False
    if raw_angle < 0:
        raw_angle = -raw_angle
        flipped = True
    raw_adjacent = target_height.Value
    raw_opposite = raw_adjacent * math.tan(math.radians(raw_angle))
    if flipped:
        raw_opposite = -raw_opposite
    opposite = raw_opposite * App.Units.MilliMetre
    return opposite