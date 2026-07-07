import FreeCAD as App
import FreeCADGui


def register():
    from construction.group_command_registerer import ConstructionGroupCommand
    from construction import group_command_registerer

    group_command_registerer.register()

    FreeCADGui.addCommand(
        ConstructionGroupCommand.__name__,
        ConstructionGroupCommand(),
    )

def append(parent: FreeCADGui.Workbench):
    from construction.group_command_registerer import ConstructionGroupCommand

    parent.appendToolbar(
        'Ava Helpers',
        [
            ConstructionGroupCommand.__name__
        ]
    )
    parent.appendMenu(
        'Ava Helpers',
        [
            ConstructionGroupCommand.__name__
        ]
    )