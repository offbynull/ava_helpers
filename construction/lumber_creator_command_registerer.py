import FreeCAD as App
import FreeCADGui


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class LumberCreatorCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Create lumber',
            'ToolTip': 'Create a piece of lumber from a predefined list.',
            'Accel': 'Shift+A,C,L',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'construction'
                / 'lumber_creator.svg'
            )
        }

    def Activated(self):
        import FreeCAD as App
        import traceback
        from logger import error

        from construction import lumber_creator
        try:
            lumber_creator.run(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


COMMANDS = [
    LumberCreatorCommand,
]


def register():
    for c in COMMANDS:
        FreeCADGui.addCommand(c.__name__, c())


def get_names():
    return [c.__name__ for c in COMMANDS]
