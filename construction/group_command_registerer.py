import FreeCAD as App
import FreeCADGui


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class ConstructionGroupCommand:
    def GetCommands(self):
        from construction import part_creator_command_registerer

        return \
            tuple(part_creator_command_registerer.get_names())

    def GetResources(self):
        from pathlib import Path

        return {
            'MenuText': 'Orientation',
            'ToolTip': 'Common reorientation workflows.',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'construction'
                / 'group_command.svg'
            )
        }


def register():
    from construction import part_creator_command_registerer

    part_creator_command_registerer.register()

    FreeCADGui.addCommand(
        ConstructionGroupCommand.__name__,
        ConstructionGroupCommand(),
    )