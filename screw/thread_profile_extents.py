from dataclasses import dataclass, field, InitVar

import FreeCAD as App

from screw.geometries.cone_frustum import ConeFrustum
from screw.geometries.cylinder import Cylinder

_ZERO_MM = 0 * App.Units.MilliMetre


@dataclass(frozen=True)
class ThreadProfileExtents:
    bbox: InitVar[App.BoundBox]
    radius: InitVar[App.Units.Quantity]

    underneath_distance: App.Units.Quantity = field(init=False)
    ontop_distance: App.Units.Quantity = field(init=False)
    beside_distance: App.Units.Quantity = field(init=False)

    def __post_init__(self, bbox: App.BoundBox, radius: App.Units.Quantity):
        object.__setattr__(
            self, "underneath_distance",
            -bbox.YMin * App.Units.MilliMetre
        )
        object.__setattr__(
            self, "ontop_distance",
            bbox.YMax * App.Units.MilliMetre
        )
        object.__setattr__(
            self, "beside_distance",
           (bbox.XMax * App.Units.MilliMetre) - radius
        )

    @property
    def height(self):
        return self.underneath_distance + self.ontop_distance

    @staticmethod
    def zero():
        return ThreadProfileExtents(App.BoundBox(0.0), _ZERO_MM)