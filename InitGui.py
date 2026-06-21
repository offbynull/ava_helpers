import FreeCAD as App
import FreeCADGui

from logger import error


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class DocumentFixedJointMaterCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Mate LCS FixedJoints (document)',
            'ToolTip': 'Reorients LCSes on a FixedJoint such that the z-axis kiss (point opposite each other) and the '
                       'y-axis point in the same direction. Applied to all FixedJoints within the active document.',
            'Accel': 'Ctrl+Shift+M, Ctrl+Shift+D',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'Resources'
                / 'icons'
                / 'document_fixed_joint_mater.svg'
            )
        }

    def Activated(self):
        import FreeCAD as App
        import traceback
        from fixed_joint_maters import document_fixed_joint_mater
        try:
            document_fixed_joint_mater.run(App.ActiveDocument)
        except Exception as exc:
            error('Failed: {}'.format(exc))
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


FreeCADGui.addCommand(
    DocumentFixedJointMaterCommand.__name__,
    DocumentFixedJointMaterCommand(),
)


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class ActiveObjectFixedJointMaterCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Mate LCS FixedJoints (active object)',
            'ToolTip': 'Reorients LCSes on a FixedJoint such that the z-axis kiss (point opposite each other) and the '
                       'y-axis point in the same direction. Applied to all FixedJoints within the active object.',
            'Accel': 'Ctrl+Shift+M, Ctrl+Shift+O',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'Resources'
                / 'icons'
                / 'active_object_fixed_joint_mater.svg'
            )
        }

    def Activated(self):
        import FreeCAD as App
        import traceback
        from fixed_joint_maters import active_object_fixed_joint_mater
        try:
            active_object_fixed_joint_mater.run(App.ActiveDocument)
        except Exception as exc:
            error('Failed: {}'.format(exc))
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


FreeCADGui.addCommand(
    ActiveObjectFixedJointMaterCommand.__name__,
    ActiveObjectFixedJointMaterCommand(),
)


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class SelectedObjectsFixedJointMaterCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Mate LCS FixedJoints (selected objects)',
            'ToolTip': 'Reorients LCSes on a FixedJoint such that the z-axis kiss (point opposite each other) and the '
                       'y-axis point in the same direction. Applied to all FixedJoints within the selected objects.',
            'Accel': 'Ctrl+Shift+M, Ctrl+Shift+S',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'Resources'
                / 'icons'
                / 'selected_objects_fixed_joint_mater.svg'
            )
        }

    def Activated(self):
        import FreeCAD as App
        import traceback
        from fixed_joint_maters import active_object_fixed_joint_mater
        try:
            active_object_fixed_joint_mater.run(App.ActiveDocument)
        except Exception as exc:
            error('Failed: {}'.format(exc))
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


FreeCADGui.addCommand(
    SelectedObjectsFixedJointMaterCommand.__name__,
    SelectedObjectsFixedJointMaterCommand(),
)


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class FixedJointMaterGroupCommand:
    def GetCommands(self):
        return (
            'DocumentFixedJointMaterCommand',
            'ActiveObjectFixedJointMaterCommand',
            'SelectedObjectsFixedJointMaterCommand'
        )

    def GetResources(self):
        from pathlib import Path

        return {
            'MenuText': 'Mate LCS FixedJoints',
            'ToolTip': 'Reorients LCSes on FixedJoints.',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'Resources'
                / 'icons'
                / 'fixed_joint_mater.svg'
            )
        }


FreeCADGui.addCommand(
    FixedJointMaterGroupCommand.__name__,
    FixedJointMaterGroupCommand(),
)


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
        / 'Resources'
        / 'icons'
        / 'ava_helpers.svg'
    )

    def Initialize(self):
        self.appendToolbar(
            'Ava Helpers',
            [
                'FixedJointMaterGroupCommand'
                # 'DocumentFixedJointMaterCommand',
                # 'ActiveObjectFixedJointMaterCommand',
                # 'SelectedObjectsFixedJointMaterCommand'
            ]
        )
        self.appendMenu(
            'Ava Helpers',
            [
                'FixedJointMaterGroupCommand'
                # 'DocumentFixedJointMaterCommand',
                # 'ActiveObjectFixedJointMaterCommand',
                # 'SelectedObjectsFixedJointMaterCommand'
            ]
        )

    def GetClassName(self):
        return 'Gui::PythonWorkbench'


FreeCADGui.addWorkbench(Workbench())
