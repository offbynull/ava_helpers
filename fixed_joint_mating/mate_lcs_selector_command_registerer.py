import FreeCAD as App
import FreeCADGui


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class MateLCSSelectorCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Select mate points',
            'ToolTip': 'Select mate points using regex.',
            'Accel': 'Shift+A,R',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'mate_lcs_selector.svg'
            )
        }

    def Activated(self):
        import FreeCAD as App
        import traceback
        from logger import error

        from fixed_joint_mating import mate_lcs_selector
        try:
            mate_lcs_selector.run(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


COMMANDS = [
    MateLCSSelectorCommand,
]


def register():
    for c in COMMANDS:
        FreeCADGui.addCommand(c.__name__, c())


def get_names():
    return [c.__name__ for c in COMMANDS]
