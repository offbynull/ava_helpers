from typing import Callable

import FreeCAD as App
import FreeCADGui as Gui
import Part

from logger import log, status
from utils.selection import SelectedElement


class FaceXYPicker:
    def __init__(
            self,
            doc: App.Document,
            obj_face: SelectedElement,
            obj_vertex: SelectedElement,
            obj_edge: SelectedElement,
            snap_x: App.Units.Quantity,
            snap_y: App.Units.Quantity,
            abort_callback: Callable,
            confirm_callback: Callable,
            new_object_creator: Callable
    ):
        self.doc = doc
        self.view = Gui.ActiveDocument.ActiveView

        assert obj_face.unresolved.parent_object == obj_vertex.unresolved.parent_object
        self.face = obj_face
        self.vertex = obj_vertex
        self.edge = obj_edge
        if self.face.unresolved.subelement_object.distToShape(Part.Vertex(self.vertex.unresolved.subelement_object.Point))[0] > 1e-4:
            raise RuntimeError('Selected vertex is not on selected face.')

        self.snap_x = snap_x
        self.snap_y = snap_y

        self.abort_callback = abort_callback
        self.confirm_callback = confirm_callback
        self.new_object_creator_and_attachor = new_object_creator

        self.lcs_obj = self.new_object_creator_and_attachor()
        self.lcs_obj_base_pl = self._get_attachment_frame_placement(self.lcs_obj)
        self.snap_pl = self._get_edge_snap_placement()
        self.last_xy = None

        self.cb_click = self.view.addEventCallback('SoMouseButtonEvent', self.on_click)
        self.cb_key = self.view.addEventCallback('SoKeyboardEvent', self.on_key)
        self.cb_move = self.view.addEventCallback('SoLocation2Event', self.on_move)

    def set_snap(self, snap_x: App.Units.Quantity, snap_y: App.Units.Quantity):
        self.snap_x = snap_x
        self.snap_y = snap_y

    @staticmethod
    def _get_attachment_frame_placement(lcs_obj):
        # FreeCAD's final global LCS placement includes both:
        #   1. the attachment/map-mode frame, derived from the selected support
        #   2. AttachmentOffset, including its Base and Rotation
        #
        # AttachmentOffset.Base X/Y are interpreted in the attachment frame,
        # not in the final visually-rotated LCS frame. If we use the final
        # placement for mouse hit conversion, an AttachmentOffset.Rotation can
        # make X/Y appear flipped or rotated.
        #
        # Backing out AttachmentOffset leaves the attachment frame placement.
        # We use that frame for snap X/Y math and for producing the offset
        # vector that FreeCAD expects in AttachmentOffset.Base.
        return lcs_obj.getGlobalPlacement().multiply(lcs_obj.AttachmentOffset.inverse())

    def move_marker(self, offset):
        # Keep the existing AttachmentOffset.Rotation. Only Base changes.
        # The offset vector was computed in the attachment frame, which is
        # exactly the coordinate system FreeCAD uses for AttachmentOffset.Base.
        self.lcs_obj.AttachmentOffset = App.Placement(
            offset,
            self.lcs_obj.AttachmentOffset.Rotation
        )
        self.doc.recompute()
        # Gui.updateGui()

    def project_to_face(self, p_scene):
        p_local = self.face.unresolved.parent_object.getGlobalPlacement().inverse().multVec(p_scene)
        dist, points, _ = self.face.unresolved.subelement_object.distToShape(Part.Vertex(p_local))
        if not points:
            return None
        return self.face.unresolved.parent_object.getGlobalPlacement().multVec(points[0][0])

    def _to_parent_body_or_self(self, obj):
        if getattr(obj, 'TypeId', '') == 'PartDesign::Body':
            return obj
        for parent in getattr(obj, 'InListRecursive', []):
            if getattr(parent, 'TypeId', '') == 'PartDesign::Body':
                return parent
        return obj

    def _get_edge_snap_placement(self):
        # The FreeCAD attachment frame is still the frame that receives the
        # final AttachmentOffset.Base value.
        #
        # However, that frame's X/Y axes may be arbitrary from the user's
        # perspective. For snapping, we build a separate frame whose origin is
        # the selected vertex and whose X axis follows the selected edge.
        #
        # If the edge is not physically connected to the vertex, its position is
        # ignored. Only its direction is used, as if the edge had been
        # translated to pass through the vertex.
        p_vertex = self.vertex.unresolved.parent_object.getGlobalPlacement().multVec(self.vertex.unresolved.subelement_object.Point)

        edge_vertices = self.edge.unresolved.subelement_object.Vertexes
        p1 = self.edge.unresolved.parent_object.getGlobalPlacement().multVec(edge_vertices[0].Point)
        p2 = self.edge.unresolved.parent_object.getGlobalPlacement().multVec(edge_vertices[-1].Point)

        x_axis = p2.sub(p1)
        if x_axis.Length < 1e-7:
            raise RuntimeError('Selected edge has zero length.')

        # Use the attachment frame's Z axis as the snap frame's Z axis. This
        # keeps the snap grid coplanar with the attachment frame while allowing
        # the X/Y directions to be user-meaningful.
        z_axis = self.lcs_obj_base_pl.Rotation.multVec(App.Vector(0, 0, 1))
        z_axis.normalize()

        if x_axis.Length < 1e-7:  # If face touches edge, this test is useless?
            raise RuntimeError('Selected edge is perpendicular to selected face.')
        x_axis.normalize()
        y_axis = z_axis.cross(x_axis)
        y_axis.normalize()

        # Build a placement whose local X/Y axes define the snap grid. Points
        # are converted into this frame for rounding, then converted back to
        # world space before being projected onto the selected face.
        m = App.Matrix()
        m.A11 = x_axis.x
        m.A21 = x_axis.y
        m.A31 = x_axis.z

        m.A12 = y_axis.x
        m.A22 = y_axis.y
        m.A32 = y_axis.z

        m.A13 = z_axis.x
        m.A23 = z_axis.y
        m.A33 = z_axis.z

        m.A14 = p_vertex.x
        m.A24 = p_vertex.y
        m.A34 = p_vertex.z

        return App.Placement(m)

    def get_snap_from_event(self, info):
        hit = self.view.getObjectInfo(info['Position'])
        if hit is None \
                or hit.get('Object') != self.face.resolved.parent_object.Name \
                or hit.get('Component') != self.face.resolved.subelement_name:
            log(f'Mouse event - no hit: {(None, None) if not hit else (hit.get("Object"), hit.get("Component"))} vs {(self.face.resolved.parent_object.Name, self.face.resolved.subelement_name)}')
            return None

        p_hit = App.Vector(
            float(hit['x']),
            float(hit['y']),
            float(hit['z'])
        )
        # Snap in the edge-derived frame, not the attachment frame. The snapped
        # point is still converted back to world space and projected to the
        # selected face before producing the final attachment-frame offset.
        p_lcs = self.snap_pl.inverse().multVec(p_hit)
        x = round(p_lcs.x / self.snap_x.Value) * self.snap_x.Value
        y = round(p_lcs.y / self.snap_y.Value) * self.snap_y.Value
        p_plane = self.snap_pl.multVec(App.Vector(x, y, 0))
        p_face = self.project_to_face(p_plane)
        if p_face is None:
            return None
        offset = self.lcs_obj_base_pl.inverse().multVec(p_face)
        return x, y, offset

    def stop(self):
        self.view.removeEventCallback('SoMouseButtonEvent', self.cb_click)
        self.view.removeEventCallback('SoKeyboardEvent', self.cb_key)
        self.view.removeEventCallback('SoLocation2Event', self.cb_move)

    def on_move(self, info):
        snap = self.get_snap_from_event(info)
        if snap is None:
            return

        xs, ys, offset = snap
        xy = (xs, ys)

        if xy == self.last_xy:
            return

        self.move_marker(offset)
        self.last_xy = xy
        status(f'Snap X={xs:.1f} mm, Y={ys:.1f} mm')

    def on_click(self, info):
        snap = self.get_snap_from_event(info)
        if snap is None:
            return

        if info.get('State') != 'DOWN':
            return

        button = str(info.get('Button', '')).upper()
        if button not in ('BUTTON1', '1', 'LEFT'):
            return

        x, y, _ = snap

        log(f' X={x}, Y={y} mm')

        self.lcs_obj = self.new_object_creator_and_attachor()
        self.lcs_obj_base_pl = self._get_attachment_frame_placement(self.lcs_obj)
        self.on_move(info)

    def on_key(self, info):
        key = str(info.get('Key', '')).upper()
        if info.get('State') == 'DOWN' and key in {'ESC', 'ESCAPE'}:
            self.abort_callback()
        # elif info.get('State') == 'DOWN' and key == 'ENTER':
        #     self.confirm_callback()
