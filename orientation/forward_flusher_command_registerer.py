import FreeCAD as App
import FreeCADGui


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class ForwardFlusherCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Forward-flush object',
            'ToolTip': 'Selecting a face along with an edge on that face and launching this command will make it so '
                       'that the object is reoriented such that the face sits flush on the XY-plane and rotated such'
                       'that edge faces the forward direction (faces -Y and is parallel to the X-axis).',
            'Accel': 'Shift+O,F',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'orientation'
                / 'forward_flusher.svg'
            )
        }

    def Activated(self):
        import FreeCAD as App
        import traceback
        from logger import error

        from orientation import forward_flusher
        try:
            forward_flusher.run(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


COMMANDS = [
    ForwardFlusherCommand,
]


def register():
    for c in COMMANDS:
        FreeCADGui.addCommand(c.__name__, c())


def get_names():
    return [c.__name__ for c in COMMANDS]
