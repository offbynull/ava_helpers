from dataclasses import dataclass, field

import FreeCAD as App

from screw.cone_frustum_parameters import ConeFrustumParameters
from screw.thread_profile_extents import ThreadProfileExtents


@dataclass
class ThreadProfileExtentsSet:
    _extents: list[ThreadProfileExtents] = field(init=False, default_factory=list)

    def add(self, extents: ThreadProfileExtents):
        self._extents.append(extents)

    @property
    def underneath_distance(self):
        d = 0 * App.Units.MilliMetre
        for e in self._extents:
            d = max(e.underneath_distance, d)
        return d

    @property
    def ontop_distance(self):
        d = 0 * App.Units.MilliMetre
        for e in self._extents:
            d = max(e.ontop_distance, d)
        return d

    @property
    def beside_distance(self):
        d = 0 * App.Units.MilliMetre
        for e in self._extents:
            d = max(e.beside_distance, d)
        return d

    def bottom_excess_distance(self, minor_cone: ConeFrustumParameters, helix_distance: App.Units.Quantity):
        excess = self.underneath_distance
        return excess

    def top_excess_distance(self, minor_cone: ConeFrustumParameters, helix_distance: App.Units.Quantity):
        excess = self.ontop_distance
        helix_distance += excess
        if helix_distance < minor_cone.distance_between_radiuses:
            return 0 * App.Units.MilliMetre
        return minor_cone.distance_between_radiuses - helix_distance

    def side_protrusion_distance(self, minor_cone: ConeFrustumParameters):
        excess = self.beside_distance
        return excess - minor_cone.bottom_radius