import FreeCAD as App
import FreeCADGui


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class ScrewCreatorCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Create screw',
            'ToolTip': 'Create a screw.',
            'Accel': 'Shift+A,C,S',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'screw'
                / 'screw_creator.svg'
            )
        }

    def Activated(self):
        import FreeCAD as App
        import traceback
        from logger import error

        from screw import screw_creator
        try:
            screw_creator.run(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


COMMANDS = [
    ScrewCreatorCommand,
]


def register():
    for c in COMMANDS:
        FreeCADGui.addCommand(c.__name__, c())


def get_names():
    return [c.__name__ for c in COMMANDS]
