import FreeCAD as App

from fixed_joint_mating.lcs_create.array import _selection
from fixed_joint_mating.lcs_create.array._array_parameters import Offset, OffsetApplicationCoordinateSystem


def update_inputs_within_varset(
        doc: App.Document,
        name_or_varset: str | App.DocumentObject,
        selection: _selection.Selection,
        spacing: float,
        offset: Offset,
):
    if isinstance(name_or_varset, str):
        varset = doc.getObject(f'{name_or_varset}_Inputs')
    else:
        varset = name_or_varset

    src = selection.source
    dst = selection.destination

    _, src_face_name = selection.source_face
    _, src_vertex_name = selection.source_vertex
    _, dst_vertex_name = selection.destination_vertex
    _, src_edge_name = selection.source_edge if selection.source_edge else (None, None)

    varset.SourceFace = src, [src_face_name]
    varset.SourceVertex = src, [src_vertex_name]
    varset.SourceEdge = src, [src_edge_name]
    varset.DestinationVertex = dst, [dst_vertex_name]
    varset.Spacing = spacing
    varset.OffsetX = offset.x
    varset.OffsetY = offset.y
    varset.OffsetZ = offset.z
    varset.GlobalOffset = offset.coordinate_system_application == OffsetApplicationCoordinateSystem.GLOBAL

    return varset


def write_inputs_to_varset(
        doc: App.Document,
        name: str,
        selection: _selection.Selection,
        spacing: float,
        offset: Offset,
):
    varset = doc.addObject('App::VarSet', f'{name}_Inputs')

    varset.addProperty('App::PropertyLinkSub', 'SourceFace', 'Inputs', '')
    varset.addProperty('App::PropertyLinkSub', 'SourceVertex', 'Inputs', '')
    varset.addProperty('App::PropertyLinkSub', 'SourceEdge', 'Inputs', '')
    varset.addProperty('App::PropertyLinkSub', 'DestinationVertex', 'Inputs', '')
    varset.addProperty('App::PropertyLength', 'Spacing', 'Inputs', '')
    varset.addProperty('App::PropertyLength', 'OffsetX', 'Inputs', '')
    varset.addProperty('App::PropertyLength', 'OffsetY', 'Inputs', '')
    varset.addProperty('App::PropertyLength', 'OffsetZ', 'Inputs', '')
    varset.addProperty('App::PropertyBool', 'GlobalOffset', '')

    update_inputs_within_varset(doc, varset, selection, spacing, offset)

    return varset


def read_inputs_from_varset(doc: App.Document, name: str) -> tuple[_selection.Selection, str, float, Offset] | None:
    varset = doc.getObject(f'{name}_Inputs')

    src, (src_vertex_name, ) = varset.SourceVertex
    _, (src_face_name, ) = varset.SourceFace
    _, (src_edge_name, ) = varset.SourceEdge
    dst, (dst_vertex_name, ) = varset.DestinationVertex

    return (
        _selection.Selection(
            src,
            (src.getSubObject(src_face_name), src_face_name),
            (src.getSubObject(src_vertex_name), src_vertex_name),
            (src.getSubObject(src_edge_name), src_edge_name),
            dst,
            (dst.getSubObject(dst_vertex_name), dst_vertex_name)
        ),
        name,
        varset.Spacing.getValueAs('mm').Value,
        Offset(
            varset.OffsetX.getValueAs('mm').Value,
            varset.OffsetY.getValueAs('mm').Value,
            varset.OffsetZ.getValueAs('mm').Value,
            OffsetApplicationCoordinateSystem.GLOBAL if varset.GlobalOffset else OffsetApplicationCoordinateSystem.LCS
        )
    )
