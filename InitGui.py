import FreeCAD as App
import FreeCADGui

from fixed_joint_mating import command_registerer as fixed_joint_mating_command_registerer
from orientation import command_registerer as orientation_command_registerer
from construction import command_registerer as construction_command_registerer

fixed_joint_mating_command_registerer.register()
orientation_command_registerer.register()
construction_command_registerer.register()


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class Workbench(FreeCADGui.Workbench):
    from pathlib import Path

    MenuText = 'Ava Helpers'
    ToolTip = 'Useful helpers, intended to automate common workflows.'
    Icon = str(
        Path(App.getUserAppDataDir())
        / 'Mod'
        / 'ava_helpers'
        / 'ava_helpers.svg'
    )

    def Initialize(self):
        from fixed_joint_mating import command_registerer as fixed_joint_mating_command_registerer
        from orientation import command_registerer as orientation_command_registerer
        from construction import command_registerer as construction_command_registerer
        fixed_joint_mating_command_registerer.append(self)
        orientation_command_registerer.append(self)
        construction_command_registerer.append(self)

    def GetClassName(self):
        return 'Gui::PythonWorkbench'


FreeCADGui.addWorkbench(Workbench())
