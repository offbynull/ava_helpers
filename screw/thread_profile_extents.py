from dataclasses import dataclass, field, InitVar

import FreeCAD as App
import Part

from screw.geometries.cone_frustum import ConeFrustum
from screw.geometries.cylinder import Cylinder

_ZERO_MM = 0 * App.Units.MilliMetre


@dataclass(frozen=True)
class ThreadProfileExtents:
    doc: InitVar[App.Document]
    sketch: InitVar[App.DocumentObject]
    minor_shape_radius: InitVar[App.Units.Quantity]

    underneath_distance: App.Units.Quantity = field(init=False)
    ontop_distance: App.Units.Quantity = field(init=False)
    beside_distance: App.Units.Quantity = field(init=False)
    point_with_max_x: tuple[App.Units.Quantity, App.Units.Quantity] = field(init=False)

    def __post_init__(self, doc: App.Document, sketch: App.DocumentObject, minor_shape_radius: App.Units.Quantity):
        doc.recompute([sketch])
        shape = sketch.Shape.copy()
        inverted_placement_matrix = sketch.Placement.inverse().toMatrix()
        shape.transformShape(inverted_placement_matrix, True)
        bbox = shape.BoundBox
        
        object.__setattr__(
            self, 'underneath_distance',
            -bbox.YMin * App.Units.MilliMetre
        )
        object.__setattr__(
            self, 'ontop_distance',
            bbox.YMax * App.Units.MilliMetre
        )
        object.__setattr__(
            self, 'beside_distance',
            (bbox.XMax * App.Units.MilliMetre) - minor_shape_radius
        )

        margin = max(bbox.XLength, bbox.YLength, 1.0) * 2
        xline = bbox.XMax + margin
        line = Part.makeLine(
            App.Vector(xline, bbox.YMin - margin, 0),
            App.Vector(xline, bbox.YMax + margin, 0),
        )
        _, points, _ = shape.distToShape(line)
        p = points[0][0]
        object.__setattr__(
            self, 'point_with_max_x',
            (
                (p.x * App.Units.MilliMetre) - minor_shape_radius,
                p.y * App.Units.MilliMetre
            )
        )

    @property
    def height(self):
        return self.underneath_distance + self.ontop_distance