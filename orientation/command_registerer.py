import FreeCAD as App
import FreeCADGui


def register(parent: FreeCADGui.Workbench):
    from orientation.group_command_registerer import OrientationGroupCommand
    from orientation import group_command_registerer

    group_command_registerer.register()

    FreeCADGui.addCommand(
        OrientationGroupCommand.__name__,
        OrientationGroupCommand(),
    )

    parent.appendToolbar(
        'Ava Helpers',
        [
            OrientationGroupCommand.__name__
        ]
    )
    parent.appendMenu(
        'Ava Helpers',
        [
            OrientationGroupCommand.__name__
        ]
    )