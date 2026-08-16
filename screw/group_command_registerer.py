import FreeCAD as App
import FreeCADGui


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class ScrewGroupCommand:
    def GetCommands(self):
        from screw import screw_creator_command_registerer
        from screw import screw_reload_command_registerer

        return \
            tuple(screw_creator_command_registerer.get_names()) \
            + tuple(screw_reload_command_registerer.get_names())

    def GetResources(self):
        from pathlib import Path

        return {
            'MenuText': 'Screw',
            'ToolTip': 'Common screw workflows.',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'screw'
                / 'group_command.svg'
            )
        }


def register():
    from screw import screw_creator_command_registerer
    from screw import screw_reload_command_registerer

    screw_creator_command_registerer.register()
    screw_reload_command_registerer.register()

    FreeCADGui.addCommand(
        ScrewGroupCommand.__name__,
        ScrewGroupCommand(),
    )