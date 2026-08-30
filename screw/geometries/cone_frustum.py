from dataclasses import dataclass
from enum import Enum
from functools import cached_property

import FreeCAD as App
import math


_ZERO_MM = 0 * App.Units.MilliMetre

_ZERO_DEG = 0 * App.Units.Degree


def _cone_frustum_to_angle(radius1: App.Units.Quantity, radius2: App.Units.Quantity, radius_distance: App.Units.Quantity):
    # This is a cone frustrum: There's a height and two radiuses. Those heights and two radiuses form a trangle - use it
    # to get the angle of the cone, from the axis.
    if radius1 == radius2:
        raise ValueError('Cylinder, not cone')
    raw_radius_small, raw_radius_large = sorted([radius1.Value, radius2.Value])
    raw_radius_distance = radius_distance.Value
    raw_angle = math.degrees(
        math.atan((raw_radius_large - raw_radius_small) / raw_radius_distance)
    )
    angle = raw_angle * App.Units.Degree
    return angle


def _cone_height_at_radius(angle: App.Units.Quantity, target_radius: App.Units.Quantity):
    raw_angle = angle.Value
    raw_opposite = target_radius.Value
    raw_adjacent = raw_opposite / math.tan(math.radians(raw_angle))
    adjacent = raw_adjacent * App.Units.MilliMetre
    return adjacent


def _cone_radius_at_height(angle: App.Units.Quantity, target_height: App.Units.Quantity):
    raw_angle = angle.Value
    raw_adjacent = target_height.Value
    raw_opposite = raw_adjacent * math.tan(math.radians(raw_angle))
    opposite = raw_opposite * App.Units.MilliMetre
    return opposite


class Direction(Enum):
    UP = 'UP'
    DOWN = 'DOWN'


@dataclass(frozen=True)
class ConeFrustum:
    bottom_radius: App.Units.Quantity
    top_radius: App.Units.Quantity
    distance_between_radiuses: App.Units.Quantity

    def __post_init__(self):
        if self.bottom_radius < _ZERO_MM:
            raise ValueError(f'{self.bottom_radius=} < 0')
        if self.top_radius < _ZERO_MM:
            raise ValueError(f'{self.top_radius=} < 0')
        if self.bottom_radius == self.top_radius:
            raise ValueError(f'Cylinder, not cone')
        if self.distance_between_radiuses <= _ZERO_MM:
            raise ValueError(f'{self.distance_between_radiuses=} <= 0')

    @cached_property
    def angle(self):
        return _cone_frustum_to_angle(
            self.bottom_radius,
            self.top_radius,
            self.distance_between_radiuses
        )

    @cached_property
    def direction(self):
        if self.bottom_radius <= self.top_radius:
            return Direction.UP
        else:
            return Direction.DOWN


    @cached_property
    def closer_radius(self):
        if self.direction == Direction.UP:
            return self.bottom_radius
        elif self.direction == Direction.DOWN:
            return self.top_radius
        else:
            raise ValueError('This should never happen')

    @cached_property
    def farther_radius(self):
        if self.direction == Direction.UP:
            return self.top_radius
        elif self.direction == Direction.DOWN:
            return self.bottom_radius
        else:
            raise ValueError('This should never happen')

    @cached_property
    def closer_distance(self):
        return self.axial_distance_from_vertex_at_radius(self.closer_radius)

    @cached_property
    def farther_distance(self):
        return self.axial_distance_from_vertex_at_radius(self.farther_radius)

    @cached_property
    def bottom_distance(self):
        return self.axial_distance_from_vertex_at_radius(self.bottom_radius)

    @cached_property
    def top_distance(self):
        return self.axial_distance_from_vertex_at_radius(self.top_radius)

    def axial_distance_from_vertex_at_radius(self, radius: App.Units.Quantity):
        if radius < _ZERO_MM:
            raise ValueError(f'{radius=} < 0')

        if self.angle == _ZERO_DEG:
            raise ValueError('Not possible - shape is cylindrical')
        return _cone_height_at_radius(
            self.angle,
            radius
        )

    def radius_at_axial_distance_from_vertex(self, distance: App.Units.Quantity):
        if distance < _ZERO_MM:
            raise ValueError(f'{distance=} < 0')

        if self.angle == _ZERO_DEG:
            return self.bottom_radius
        else:
            return _cone_radius_at_height(
                self.angle,
                distance
            )

    def widen_bottom(self, radius_offset: App.Units.Quantity):
        return ConeFrustum(
            self.bottom_radius + radius_offset,
            self.top_radius,
            self.distance_between_radiuses
        )

    def widen_top(self, radius_offset: App.Units.Quantity):
        return ConeFrustum(
            self.bottom_radius,
            self.top_radius + radius_offset,
            self.distance_between_radiuses
        )

    def widen_closer(self, radius_offset: App.Units.Quantity):
        if self.closer_radius + radius_offset > self.farther_radius:
            raise ValueError(f'{self.closer_radius + radius_offset=} > {self.farther_radius}')
        if self.direction == Direction.UP:
            return self.widen_bottom(radius_offset)
        elif self.direction == Direction.DOWN:
            return self.widen_top(radius_offset)
        else:
            raise ValueError('This should never happen')

    def widen_farther(self, radius_offset: App.Units.Quantity):
        if self.farther_radius + radius_offset < self.closer_radius:
            raise ValueError(f'{self.farther_radius + radius_offset=} < {self.closer_radius}')
        if self.direction == Direction.UP:
            return self.widen_top(radius_offset)
        elif self.direction == Direction.DOWN:
            return self.widen_bottom(radius_offset)
        else:
            raise ValueError('This should never happen')

    def widen(self, radius_offset: App.Units.Quantity):
        return ConeFrustum(
            self.bottom_radius + radius_offset,
            self.top_radius + radius_offset,
            self.distance_between_radiuses
        )

    def shift_bottom(self, distance_offset: App.Units.Quantity):
        return self.with_bottom_distance(self.bottom_distance + distance_offset)

    def shift_top(self, distance_offset: App.Units.Quantity):
        return self.with_top_distance(self.top_distance + distance_offset)

    def shift_closer(self, distance_offset: App.Units.Quantity):
        if self.closer_distance + distance_offset > self.farther_distance:
            raise ValueError(f'{self.closer_distance + distance_offset=} > {self.farther_distance}')
        if self.direction == Direction.UP:
            return self.shift_bottom(distance_offset)
        elif self.direction == Direction.DOWN:
            return self.shift_top(distance_offset)
        else:
            raise ValueError('This should never happen')

    def shift_farther(self, distance_offset: App.Units.Quantity):
        if self.farther_distance + distance_offset < self.closer_distance:
            raise ValueError(f'{self.farther_distance + distance_offset=} < {self.closer_distance}')
        if self.direction == Direction.UP:
            return self.shift_top(distance_offset)
        elif self.direction == Direction.DOWN:
            return self.shift_bottom(distance_offset)
        else:
            raise ValueError('This should never happen')

    def shift(self, distance_offset: App.Units.Quantity):
        return ConeFrustum(
            self.radius_at_axial_distance_from_vertex(self.bottom_distance + distance_offset),
            self.radius_at_axial_distance_from_vertex(self.top_distance + distance_offset),
            self.distance_between_radiuses
        )

    def with_bottom_radius(self, radius: App.Units.Quantity):
        return ConeFrustum(
            radius,
            self.top_radius,
            self.distance_between_radiuses
        )

    def with_top_radius(self, radius: App.Units.Quantity):
        return ConeFrustum(
            self.bottom_radius,
            radius,
            self.distance_between_radiuses
        )

    def with_closer_radius(self, radius: App.Units.Quantity):
        if self.direction == Direction.UP:
            return self.with_bottom_radius(radius)
        elif self.direction == Direction.DOWN:
            return self.with_top_radius(radius)
        else:
            raise ValueError('This should never happen')

    def with_farther_radius(self, radius: App.Units.Quantity):
        if self.direction == Direction.UP:
            return self.with_top_radius(radius)
        elif self.direction == Direction.DOWN:
            return self.with_bottom_radius(radius)
        else:
            raise ValueError('This should never happen')

    def with_bottom_distance(self, distance: App.Units.Quantity):
        if (self.direction == Direction.UP and distance >= self.top_distance) \
                or (self.direction == Direction.DOWN and distance <= self.top_distance):
            raise ValueError(f'{distance=} bleeds past {self.top_distance=}')
        bottom_radius = self.radius_at_axial_distance_from_vertex(distance)
        return ConeFrustum(
            bottom_radius,
            self.top_radius,
            abs(self.top_distance - distance)
        )

    def with_top_distance(self, distance: App.Units.Quantity):
        if (self.direction == Direction.UP and self.bottom_distance >= distance) \
                or (self.direction == Direction.DOWN and self.bottom_distance <= distance):
            raise ValueError(f'{distance=} bleeds past {self.bottom_distance=}')
        top_radius = self.radius_at_axial_distance_from_vertex(distance)
        return ConeFrustum(
            self.bottom_radius,
            top_radius,
            abs(distance - self.bottom_distance)
        )

    def with_distance_from_bottom(self, distance: App.Units.Quantity):
        if distance < _ZERO_MM:
            raise ValueError(f'{distance=} < 0')

        if self.direction == Direction.UP:
            top_radius = self.radius_at_axial_distance_from_vertex(self.bottom_distance + distance)
        elif self.direction == Direction.DOWN:
            if distance > self.bottom_distance:
                raise ValueError(f'{distance=} too large vs {self.bottom_distance=}')
            top_radius = self.radius_at_axial_distance_from_vertex(self.bottom_distance - distance)
        else:
            raise ValueError('This should never happen')

        return ConeFrustum(
            self.bottom_radius,
            top_radius,
            distance
        )

    def with_distance_from_top(self, distance: App.Units.Quantity):
        if distance < _ZERO_MM:
            raise ValueError(f'{distance=} < 0')

        if self.direction == Direction.UP:
            if distance > self.top_distance:
                raise ValueError(f'{distance=} too large vs {self.top_distance=}')
            bottom_radius = self.radius_at_axial_distance_from_vertex(self.top_distance - distance)
        elif self.direction == Direction.DOWN:
            bottom_radius = self.radius_at_axial_distance_from_vertex(self.top_distance + distance)
        else:
            raise ValueError('This should never happen')

        return ConeFrustum(
            bottom_radius,
            self.top_radius,
            distance
        )

    def with_distance_from_closer(self, distance: App.Units.Quantity):
        if self.direction == Direction.UP:
            return self.with_distance_from_bottom(distance)
        elif self.direction == Direction.DOWN:
            return self.with_distance_from_top(distance)
        else:
            raise ValueError('This should never happen')

    def with_distance_from_farther(self, distance: App.Units.Quantity):
        if self.direction == Direction.UP:
            return self.with_distance_from_top(distance)
        elif self.direction == Direction.DOWN:
            return self.with_distance_from_bottom(distance)
        else:
            raise ValueError('This should never happen')


    def create_partdesign_additive_cone(self, body: App.DocumentObject, name: str):
        ret = body.newObject(f'PartDesign::AdditiveCone', name)
        ret.Radius1 = self.bottom_radius
        ret.Radius2 = self.top_radius
        ret.Height = self.distance_between_radiuses
        ret.Angle = 360 * App.Units.Degree
        return ret

    def create_partdesign_subtractive_cone(self, body: App.DocumentObject, name: str):
        ret = body.newObject(f'PartDesign::SubtractiveCone', name)
        ret.Radius1 = self.bottom_radius
        ret.Radius2 = self.top_radius
        ret.Height = self.distance_between_radiuses
        ret.Angle = 360 * App.Units.Degree
        return ret

    def create_partdesign_additive_helix(
            self,
            body: App.DocumentObject,
            name: str,
            sketch: App.DocumentObject,
            lead: App.Units.Quantity,
            left_handed: bool
    ):
        ret = body.newObject('PartDesign::AdditiveHelix', name)
        ret.Profile = (sketch, ['', ])
        ret.ReferenceAxis = (sketch, ['V_Axis'])
        ret.Mode = 0
        ret.Pitch = lead  # + (0.0001 * App.Units.MilliMetre)  # Need 0.0001mm or else the geometry breaks
        ret.Height = self.distance_between_radiuses
        ret.Angle = self.angle if self.direction == Direction.UP else -self.angle
        ret.Growth = 0
        ret.LeftHanded = left_handed
        ret.Reversed = 0
        return ret