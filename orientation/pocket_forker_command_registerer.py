import FreeCAD as App
import FreeCADGui


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class ForkerCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Pocket-fork object',
            'ToolTip': 'Fork an object by creating a new body that has that object as its base feature and apply a '
                       'pocket.',
            'Accel': 'Shift+A,F,P',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'orientation'
                / 'pocket_forker.svg'
            )
        }

    def Activated(self):
        import FreeCAD as App
        import traceback
        from logger import error

        from orientation import pocket_forker
        try:
            pocket_forker.run(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


COMMANDS = [
    ForkerCommand,
]


def register():
    for c in COMMANDS:
        FreeCADGui.addCommand(c.__name__, c())


def get_names():
    return [c.__name__ for c in COMMANDS]
