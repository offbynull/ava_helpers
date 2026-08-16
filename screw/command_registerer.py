import FreeCAD as App
import FreeCADGui


def register():
    from screw.group_command_registerer import ScrewGroupCommand
    from screw import group_command_registerer

    group_command_registerer.register()

    FreeCADGui.addCommand(
        ScrewGroupCommand.__name__,
        ScrewGroupCommand(),
    )

def append(parent: FreeCADGui.Workbench):
    from screw.group_command_registerer import ScrewGroupCommand

    parent.appendToolbar(
        'Ava Helpers',
        [
            ScrewGroupCommand.__name__
        ]
    )
    parent.appendMenu(
        'Ava Helpers',
        [
            ScrewGroupCommand.__name__
        ]
    )