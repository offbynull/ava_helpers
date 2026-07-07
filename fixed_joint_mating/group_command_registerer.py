import FreeCAD as App
import FreeCADGui


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class FixedJointMaterGroupCommand:
    def GetCommands(self):
        from fixed_joint_mating.lcs_visibility import lcs_visibility_command_registerer
        from fixed_joint_mating.lcs_select import lcs_selector_command_registerer
        from fixed_joint_mating.lcs_join import lcs_join_command_registerer
        from fixed_joint_mating.lcs_create import lcs_create_command_registerer

        return \
            tuple(lcs_create_command_registerer.get_names()) + \
            tuple(lcs_join_command_registerer.get_names()) + \
            tuple(lcs_selector_command_registerer.get_names()) + \
            tuple(lcs_visibility_command_registerer.get_names())

    def GetResources(self):
        from pathlib import Path

        return {
            'MenuText': 'Mater LCS',
            'ToolTip': 'Mater LCS operations.',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'group_command.svg'
            )
        }


def register():
    from fixed_joint_mating.lcs_visibility import lcs_visibility_command_registerer
    from fixed_joint_mating.lcs_select import lcs_selector_command_registerer
    from fixed_joint_mating.lcs_join import lcs_join_command_registerer
    from fixed_joint_mating.lcs_create import lcs_create_command_registerer

    lcs_create_command_registerer.register()
    lcs_join_command_registerer.register()
    lcs_selector_command_registerer.register(),
    lcs_visibility_command_registerer.register()

    FreeCADGui.addCommand(
        FixedJointMaterGroupCommand.__name__,
        FixedJointMaterGroupCommand(),
    )