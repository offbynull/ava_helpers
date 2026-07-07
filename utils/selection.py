from dataclasses import dataclass
from enum import Enum

import FreeCAD as App
import FreeCADGui as Gui

from logger import log


class SubelementType(Enum):
    FACE = 'Face'
    VERTEX = 'Vertex'
    EDGE = 'Edge'


@dataclass
class SelectedElementOption:
    parent_object: App.DocumentObject
    subelement_object: App.DocumentObject
    subelement_name: str


@dataclass
class SelectedElement:
    type: SubelementType
    unresolved: SelectedElementOption
    resolved: SelectedElementOption


def extract_selection_inputs(doc: App.Document) -> list[SelectedElement]:
    picked = []

    unres_selections = Gui.Selection.getSelectionEx('', 0)
    res_selections = Gui.Selection.getSelectionEx('', 1)

    for unres_selection, res_selection in zip(unres_selections, res_selections):
        for unres_subelem_name, unres_subelem_obj, res_subelem_name, res_subelem_obj in zip(
                unres_selection.SubElementNames,
                unres_selection.SubObjects,
                res_selection.SubElementNames,
                res_selection.SubObjects
        ):
            shape_type = unres_subelem_obj.ShapeType
            log(f'{shape_type}')
            log(f'{set(t.value for t in SubelementType)}')
            if shape_type in {t.value for t in SubelementType}:
                unres_obj = unres_selection.Object
                res_obj = res_selection.Object
                picked.append(
                    SelectedElement(
                        type=SubelementType(shape_type),
                        unresolved=SelectedElementOption(
                            unres_obj,
                            unres_obj.getSubObject(unres_subelem_name),
                            unres_subelem_name
                        ),
                        resolved=SelectedElementOption(
                            res_obj,
                            res_obj.getSubObject(res_subelem_name),
                            res_subelem_name
                        )
                    )
                )
    log(f'{picked=}')
    return picked