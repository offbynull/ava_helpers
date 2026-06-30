import FreeCAD as App
import FreeCADGui


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class MatePointSingleJoinerCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Join mate points',
            'ToolTip': 'Join together two mate point LCSes using a fixed joint.',
            'Accel': 'Shift+A, J, J',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'mate_lcs_joiner_single.svg'
            )
        }

    def Activated(self):
        from logger import error
        import FreeCAD as App
        import traceback

        
        from fixed_joint_mating import mate_lcs_joiner
        try:
            mate_lcs_joiner.run_single(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class MatePointMultiJoinerCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Join mate points (multiple)',
            'ToolTip': 'Join together two sets of mate point LCSes, each using a fixed joint. The selected LCSes are '
                       'split into two lists: The first half of the selections and the second half of the '
                       'selections. Each index within in the first list is joined with the the corresponding index in '
                       'the second list.',
            'Accel': 'Shift+A, J, S',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'mate_lcs_joiner_multi.svg'
            )
        }

    def Activated(self):
        from logger import error
        import FreeCAD as App
        import traceback

        from fixed_joint_mating import mate_lcs_joiner
        try:
            mate_lcs_joiner.run_multi(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True

COMMANDS = [
    MatePointSingleJoinerCommand,
    MatePointMultiJoinerCommand
]

def register():
    for c in COMMANDS:
        FreeCADGui.addCommand(c.__name__, c())


def get_names():
    return [c.__name__ for c in COMMANDS]
