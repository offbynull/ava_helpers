from dataclasses import dataclass

import FreeCAD as App

from screw.geometries.cone_frustum import ConeFrustum


@dataclass(frozen=True)
class LeadInParameters:
    tip_radius_offset: App.Units.Quantity
    distance_between_radiuses: App.Units.Quantity

    def apply_to_bottom(self, minor_cone: ConeFrustum):
        tip_radius = minor_cone.bottom_radius + self.tip_radius_offset
        if minor_cone.angle != 0:
            interior_radius_height = minor_cone.bottom_height + self.distance_between_radiuses
            interior_radius = minor_cone.radius_at_axial_distance_from_vertex(interior_radius_height)
        else:
            interior_radius = minor_cone.bottom_radius
        return ConeFrustum(tip_radius, interior_radius, self.distance_between_radiuses)

    def apply_to_top(self, minor_cone: ConeFrustum):
        tip_radius = minor_cone.top_radius + self.tip_radius_offset
        if minor_cone.angle != 0:
            interior_radius_height = minor_cone.top_height - self.distance_between_radiuses
            interior_radius = minor_cone.radius_at_axial_distance_from_vertex(interior_radius_height)
        else:
            interior_radius = minor_cone.top_radius
        return ConeFrustum(interior_radius, tip_radius, self.distance_between_radiuses)
