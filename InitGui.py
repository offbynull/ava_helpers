import FreeCAD as App
import FreeCADGui


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
        from fixed_joint_mating import command_registerer
        command_registerer.register(self)

    def GetClassName(self):
        return 'Gui::PythonWorkbench'


FreeCADGui.addWorkbench(Workbench())
