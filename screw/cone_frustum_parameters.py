from dataclasses import dataclass
from functools import cached_property

import FreeCAD as App
import math


def _cone_frustum_to_angle(radius1: App.Units.Quantity, radius2: App.Units.Quantity, radius_distance: App.Units.Quantity):
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


def _cone_height_at_radius(angle: App.Units.Quantity, target_radius: App.Units.Quantity):
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


def _cone_radius_at_height(angle: App.Units.Quantity, target_height: App.Units.Quantity):
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



@dataclass(frozen=True)
class ConeFrustumParameters:
    bottom_radius: App.Units.Quantity
    top_radius: App.Units.Quantity
    distance_between_radiuses: App.Units.Quantity

    @cached_property
    def angle(self):
        return _cone_frustum_to_angle(
            self.bottom_radius,
            self.top_radius,
            self.distance_between_radiuses
        )

    @cached_property
    def bottom_height(self):
        return self.height_at_radius(self.bottom_radius)

    @cached_property
    def top_height(self):
        return self.height_at_radius(self.top_radius)

    def height_at_radius(self, radius: App.Units.Quantity):
        return _cone_height_at_radius(
            self.angle,
            radius
        )

    def radius_at_height(self, height: App.Units.Quantity):
        return _cone_radius_at_height(
            self.angle,
            height
        )





