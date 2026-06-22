import FreeCAD as App
import FreeCADGui


def register(parent: FreeCADGui.Workbench):
    from fixed_joint_mating.group_command_registerer import FixedJointMaterGroupCommand
    from fixed_joint_mating import group_command_registerer

    group_command_registerer.register()

    FreeCADGui.addCommand(
        FixedJointMaterGroupCommand.__name__,
        FixedJointMaterGroupCommand(),
    )

    parent.appendToolbar(
        'Ava Helpers',
        [
            FixedJointMaterGroupCommand.__name__
        ]
    )
    parent.appendMenu(
        'Ava Helpers',
        [
            FixedJointMaterGroupCommand.__name__
        ]
    )