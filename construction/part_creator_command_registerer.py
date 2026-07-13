import FreeCAD as App
import FreeCADGui


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class LumberCreatorCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Create part',
            'ToolTip': 'Create a construction part (e.g., piece of lumber) from a predefined list.',
            'Accel': 'Shift+A,C,P',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'construction'
                / 'part_creator.svg'
            )
        }

    def Activated(self):
        import FreeCAD as App
        import traceback
        from logger import error

        from construction import part_creator
        try:
            part_creator.run(App.ActiveDocument)
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
