from dataclasses import dataclass
from enum import Enum

import FreeCAD as App





class OffsetApplicationCoordinateSystem(Enum):
    GLOBAL = 'GLOBAL'
    LCS = 'LCS'


@dataclass
class Offset:
    x: float
    y: float
    z: float
    coordinate_system_application: OffsetApplicationCoordinateSystem
