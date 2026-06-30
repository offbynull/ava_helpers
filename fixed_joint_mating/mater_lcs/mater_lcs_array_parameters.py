from dataclasses import dataclass
from enum import Enum

import FreeCAD as App


@dataclass
class Selection:
    source: App.DocumentObject
    source_face: tuple[App.DocumentObject, str]
    source_vertex: tuple[App.DocumentObject, str]
    source_edge: tuple [App.DocumentObject, str] | None
    destination: App.DocumentObject
    destination_vertex: tuple[App.DocumentObject, str]


class OffsetApplicationCoordinateSystem(Enum):
    GLOBAL = 'GLOBAL'
    LCS = 'LCS'


@dataclass
class Offset:
    x: float
    y: float
    z: float
    coordinate_system_application: OffsetApplicationCoordinateSystem
