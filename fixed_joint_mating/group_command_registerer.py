import FreeCAD as App
import FreeCADGui


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class FixedJointMaterGroupCommand:
    def GetCommands(self):
        from fixed_joint_mating import document_command_registerer, active_object_command_registerer, \
            selected_objects_command_registerer, mate_point_creator_command_registerer

        return \
            tuple(mate_point_creator_command_registerer.get_names()) + \
            tuple(selected_objects_command_registerer.get_names()) + \
            tuple(active_object_command_registerer.get_names()) + \
            tuple(document_command_registerer.get_names())


    def GetResources(self):
        from pathlib import Path

        return {
            'MenuText': 'Mate LCS FixedJoints',
            'ToolTip': 'Reorients LCSes on FixedJoints.',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'group_command.svg'
            )
        }


def register():
    from fixed_joint_mating import document_command_registerer, active_object_command_registerer, \
        selected_objects_command_registerer, mate_point_creator_command_registerer

    mate_point_creator_command_registerer.register()
    selected_objects_command_registerer.register()
    active_object_command_registerer.register()
    document_command_registerer.register()

    FreeCADGui.addCommand(
        FixedJointMaterGroupCommand.__name__,
        FixedJointMaterGroupCommand(),
    )