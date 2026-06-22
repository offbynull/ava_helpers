import FreeCAD as App
import FreeCADGui


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class OrientationGroupCommand:
    def GetCommands(self):
        from orientation import forward_flusher_command_registerer, origin_centerer_command_registerer

        return \
            tuple(forward_flusher_command_registerer.get_names()) + \
            tuple(origin_centerer_command_registerer.get_names())

    def GetResources(self):
        from pathlib import Path

        return {
            'MenuText': 'Orientation',
            'ToolTip': 'Common reorientation workflows.',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'orientation'
                / 'group_command.svg'
            )
        }


def register():
    from orientation import forward_flusher_command_registerer, origin_centerer_command_registerer

    forward_flusher_command_registerer.register()
    origin_centerer_command_registerer.register()

    FreeCADGui.addCommand(
        OrientationGroupCommand.__name__,
        OrientationGroupCommand(),
    )