import FreeCAD as App
import FreeCADGui


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class MatePointCreatorCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Create mate point',
            'ToolTip': 'Create a "mate point" LCS and attach it to the selected face and vertex using "XY tangent to '
                       'surface" attachment mode . The face and vertex must be on the same object. The resulting LCS '
                       'will be oriented such that the Z-axis maps to the face\'s normal vector.\n'
                       '\n'
                       'If an edge is also selected, the Y-axis of the LCS will point towards that edge. Otherwise, '
                       'the Y-axis will point as close as possible to the parent coordinate system\'s positive Z '
                       'direction.',
            'Accel': 'Shift+Z, Z',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'selected_objects_fixed_joint_mater.svg'
            )
        }

    def Activated(self):
        from logger import error
        import FreeCAD as App
        import traceback

        
        from fixed_joint_mating import mate_point_creator
        try:
            mate_point_creator.run_single(App.ActiveDocument)
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
            'MenuText': 'Create mate points along an edge',
            'ToolTip': 'Create an array of "mate point" LCS and attach it them to the selected face and vertex using '
                       '"XY tangent to surface" attachment mode. Expected selections are ...\n'
                       '\n'
                       '* a face.\n'
                       '* two vertices.\n'
                       '* an edge (optional).\n'
                       '\n'
                       'The face and the first vertex must be on the same object. The resulting LCSes will be oriented '
                       'such that the Z-axis maps to the face\'s normal vector. If an edge is also selected, the '
                       'Y-axis of the LCS will point towards that edge. Otherwise, the Y-axis will point as close as '
                       'possible to the parent coordinate system\'s positive Z direction.\n'
                       '\n'
                       'The second vertex does not have to be on the same object as the first. The mate points are '
                       'created along the line made up by the two vertices, from the first vertex to the second.',
            'Accel': 'Shift+Z, Z',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'selected_objects_fixed_joint_mater.svg'
            )
        }

    def Activated(self):
        from logger import error
        import FreeCAD as App
        import traceback


        from fixed_joint_mating import mate_point_creator
        try:
            mate_point_creator.run_array(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


COMMANDS = [
    MatePointCreatorCommand,
    MatePointArrayCreatorCommand
]

def register():
    for c in COMMANDS:
        FreeCADGui.addCommand(c.__name__, c())


def get_names():
    return [c.__name__ for c in COMMANDS]
