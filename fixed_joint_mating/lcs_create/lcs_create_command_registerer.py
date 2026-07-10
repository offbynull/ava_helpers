import FreeCAD as App
import FreeCADGui


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class MatePointVertexCreatorCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Create mate point on vertices',
            'ToolTip': 'Create a mater LCS and attach it to the selected face and vertices using "XY tangent to '
                       'surface" attachment mode. The face and vertices must be on the same object. The resulting LCS '
                       'will be oriented such that the Z-axis maps to the face\'s normal vector.\n'
                       '\n'
                       'If an edge is also selected, the Y-axis of the LCS will point towards that edge. Otherwise, '
                       'the Y-axis will point as close as possible to the parent coordinate system\'s positive Z '
                       'direction.',
            'Accel': 'Shift+A, M, V',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'lcs_create'
                / 'vertex'
                / 'lcs_creator_vertex.svg'
            )
        }

    def Activated(self):
        from logger import error
        import FreeCAD as App
        import traceback

        from fixed_joint_mating.lcs_create.vertex import lcs_creator_vertex
        try:
            lcs_creator_vertex.run(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class MatePointPickingCreatorCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Create mate point on face',
            'ToolTip': 'Create mater LCSes by clicking on a face. Expected selections are ...\n'
                       '\n'
                       '1. a face.\n'
                       '2. a vertex attached to the face.\n'
                       '3. an edge.\n'
                       '4. an edge (optional).\n'
                       '\n'
                       'The face and the first vertex must be on the same object. Once active, moving the mouse over '
                       'the face causes an LCS to follow the mouse, snapping to a grid. The grid\'s X-axis is parallel '
                       'to the first selected edge / Y-axis is perpendicular to the first selected edge. Clicking the '
                       'mouse button on the face drops the moving LCS at that point and creates a new moving LCS for a '
                       'subsequent click/drop.\n'
                       '\n'
                       'Each LCS attaches to the selected face and vertex using "XY tangent to surface" attachment '
                       'mode. The resulting LCSes will be oriented such that the Z-axis maps to the face\'s normal '
                       'vector.\n'
                       '\n'
                       'If a 2nd edge is also selected, the Y-axis of the LCS will point towards that edge. Otherwise, '
                       'the Y-axis will point to the 1st selected edge.',
            'Accel': 'Shift+A, M, F',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'lcs_create'
                / 'pick'
                / 'lcs_creator_pick.svg'
            )
        }

    def Activated(self):
        from logger import error
        import FreeCAD as App
        import traceback

        from fixed_joint_mating.lcs_create.pick import lcs_creator_pick
        try:
            lcs_creator_pick.run(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class MatePointArrayCreatorCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Create mate point array',
            'ToolTip': 'Create an array of mater LCS and attach it them to the selected face and vertex using '
                       '"XY tangent to surface" attachment mode. Expected selections are ...\n'
                       '\n'
                       '1. a face.\n'
                       '2. two vertices.\n'
                       '3. an edge (optional).\n'
                       '\n'
                       'The face and the first vertex must be on the same object. The resulting LCSes will be oriented '
                       'such that the Z-axis maps to the face\'s normal vector. If an edge is also selected, the '
                       'Y-axis of the LCS will point towards that edge. Otherwise, the Y-axis will point as close as '
                       'possible to the parent coordinate system\'s positive Z direction.\n'
                       '\n'
                       'The second vertex does not have to be on the same object as the first. The maters are '
                       'created along the line made up by the two vertices, from the first vertex to the second.',
            'Accel': 'Shift+A, M, A',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'lcs_create'
                / 'array'
                / 'lcs_array_creator.svg'
            )
        }

    def Activated(self):
        from logger import error
        import FreeCAD as App
        import traceback

        from fixed_joint_mating.lcs_create.array import lcs_array_creator
        try:
            lcs_array_creator.run(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


COMMANDS = [
    MatePointVertexCreatorCommand,
    MatePointPickingCreatorCommand,
    MatePointArrayCreatorCommand
]

def register():
    for c in COMMANDS:
        FreeCADGui.addCommand(c.__name__, c())


def get_names():
    return [c.__name__ for c in COMMANDS]
