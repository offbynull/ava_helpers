from dataclasses import dataclass
from functools import cached_property

import FreeCAD as App

from screw.thread_profile_extents import ThreadProfileExtents

_ZERO_MM = 0 * App.Units.MilliMetre

_ZERO_DEG = 0 * App.Units.Degree


@dataclass(frozen=True)
class Cylinder:
    radius: App.Units.Quantity
    distance_between_ends: App.Units.Quantity

    def __post_init__(self):
        if self.radius <= _ZERO_MM:
            raise ValueError(f'{self.radius=} < 0')
        if self.distance_between_ends <= _ZERO_MM:
            raise ValueError(f'{self.distance_between_ends=} <= 0')

    @cached_property
    def bottom_radius(self):
        return self.radius

    @cached_property
    def top_radius(self):
        return self.radius

    @cached_property
    def distance_between_radiuses(self):
        return self.distance_between_ends

    @cached_property
    def angle(self):
        return _ZERO_DEG

    def widen(self, radius_offset: App.Units.Quantity):
        return Cylinder(
            self.radius + radius_offset,
            self.distance_between_ends
        )

    def widen_bottom(self, radius_offset: App.Units.Quantity):
        return self.widen(radius_offset)

    def widen_top(self, radius_offset: App.Units.Quantity):
        return self.widen(radius_offset)

    def widen_closer(self, radius_offset: App.Units.Quantity):
        return self.widen(radius_offset)

    def widen_farther(self, radius_offset: App.Units.Quantity):
        return self.widen(radius_offset)

    def lengthen(self, distance_offset: App.Units.Quantity):
        return Cylinder(
            self.radius,
            self.distance_between_ends + distance_offset
        )

    def with_radius(self, radius: App.Units.Quantity):
        return Cylinder(
            radius,
            self.distance_between_ends
        )

    def with_distance(self, distance: App.Units.Quantity):
        return Cylinder(
            self.radius,
            distance
        )

    def with_distance_from_bottom(self, distance: App.Units.Quantity):
        return self.with_distance(distance)

    def with_distance_from_top(self, distance: App.Units.Quantity):
        return self.with_distance(distance)


    def create_partdesign_additive_cone(self, body: App.DocumentObject, name: str):
        ret = body.newObject(f'PartDesign::AdditiveCone', name)
        ret.Radius1 = self.radius
        ret.Radius2 = self.radius
        ret.Height = self.distance_between_ends
        ret.Angle = 360 * App.Units.Degree
        return ret

    def create_partdesign_subtractive_cone(self, body: App.DocumentObject, name: str):
        ret = body.newObject(f'PartDesign::SubtractiveCone', name)
        ret.Radius1 = self.radius
        ret.Radius2 = self.radius
        ret.Height = self.distance_between_ends
        ret.Angle = 360 * App.Units.Degree
        return ret

    def create_partdesign_additive_cylinder(self, body: App.DocumentObject, name: str):
        ret = body.newObject(f'PartDesign::AdditiveCylinder', name)
        ret.Radius = self.radius
        ret.Height = self.distance_between_ends
        ret.Angle = 360 * App.Units.Degree
        return ret

    def create_partdesign_subtractive_cylinder(self, body: App.DocumentObject, name: str):
        ret = body.newObject(f'PartDesign::SubtractiveCylinder', name)
        ret.Radius = self.radius
        ret.Height = self.distance_between_ends
        ret.Angle = 360 * App.Units.Degree
        return ret
