import FreeCAD as App
import FreeCADGui as Gui

from fixed_joint_mating.lcs_create.pick._face_picker import FaceXYPicker
from fixed_joint_mating.lcs_create.pick._picker_task_panel import PickerTaskPanel
from fixed_joint_mating.lcs_utils import lcs_creator, lcs_attacher, lcs_attachment_y_facing_edge_orienter, \
    lcs_attachment_y_facing_positive_z_orienter, lcs_detacher
from fixed_joint_mating.lcs_utils.lcs_identifier import MATER_LCS_IDENTIFIER
from logger import warn, error, log
from utils.selection import extract_selection_inputs, SubelementType
from utils.unit import as_default_unit


def run(doc: App.Document | None = None):
    if doc is None:
        warn('AvaHelpersWorkbench: no active document.')
        return

    selection = extract_selection_inputs(doc)
    faces = [p for p in selection if p.type == SubelementType.FACE]
    verts = [p for p in selection if p.type == SubelementType.VERTEX]
    edges = [p for p in selection if p.type == SubelementType.EDGE]
    if len(faces) != 1 or len(verts) != 1 or len(edges) not in {1, 2}:
        error('Select exactly one face and one vertex, and optionally one edge.')
        return
    face, = faces
    vertex, = verts
    edge_x_axis = edges[0]
    edge_y_direction = edges[1] if len(edges) > 1 else None
    obj = face.unresolved.parent_object
    if obj != vertex.unresolved.parent_object \
            or obj != edge_x_axis.unresolved.parent_object \
            or (edge_y_direction is not None and obj != edge_y_direction.unresolved.parent_object):
        error('Selected face, vertex, and edge must be on the same object.')
        return
    log(f'Selected entities: {face=}, {vertex=}, {edge_x_axis=} {edge_y_direction}')

    doc.openTransaction('Create mater LCS multi')

    face_picker = None
    lcses = []

    def abort_callback():
        face_picker.stop()
        doc.abortTransaction()
        Gui.Control.closeDialog()

    def confirm_callback():
        face_picker.stop()
        # Remove last LCS (it's unset)
        doc.removeObject(face_picker.lcs_obj.Name)
        nonlocal lcses
        lcses = lcses[:-1]
        # Detach LCSes
        for lcs in lcses:
            lcs_detacher.run(doc, lcs)
        doc.commitTransaction()
        Gui.Control.closeDialog()

    default_name = obj.Label + ' - ' + MATER_LCS_IDENTIFIER
    def update_callback(name_: str, snap_xy: App.Units.Quantity):
        nonlocal default_name
        face_picker.set_snap(snap_xy)
        default_name = name_

    def create_and_attach():
        lcs = lcs_creator.run(doc, default_name)
        lcs_attacher.run(doc, lcs, obj, face.unresolved.subelement_name, vertex.unresolved.subelement_name)
        if edge_y_direction is not None:
            lcs_attachment_y_facing_edge_orienter.run(doc, lcs, obj, face.unresolved.subelement_name,
                                                      edge_y_direction.unresolved.subelement_name)
        else:
            lcs_attachment_y_facing_positive_z_orienter.run(doc, lcs)
        lcses.append(lcs)
        return lcs

    default_snap_xy = as_default_unit(1.0)
    face_picker = FaceXYPicker(
        doc,
        face,
        vertex,
        edge_x_axis,
        default_snap_xy,
        abort_callback,
        confirm_callback,
        create_and_attach
    )

    panel = PickerTaskPanel(
        abort_callback,
        confirm_callback,
        update_callback,
        default_name,
        default_snap_xy
    )

    Gui.Control.showDialog(panel)