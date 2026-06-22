import FreeCAD as App
import FreeCADGui


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class SelectedObjectsFixedJointMaterCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Mate LCS FixedJoints (selected objects)',
            'ToolTip': 'Reorients LCSes on a FixedJoint such that the z-axis kiss (point opposite each other) and the '
                       'y-axis point in the same direction. Applied to all FixedJoints within the selected objects.',
            'Accel': 'Shift+Z, Z',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'selected_objects_fixed_joint_mater.svg'
            )
        }

    def Activated(self):
        from logger import error
        import FreeCAD as App
        import traceback

        
        from fixed_joint_mating import selected_objects_fixed_joint_mater
        try:
            selected_objects_fixed_joint_mater.run(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class SelectedObjectsFixedJointMateVisibilityShowerCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Mate LCS FixedJoints - visible show (selected objects)',
            'ToolTip': 'Mate LCSes are made visible. Applied to all FixedJoints within the selected objects.',
            'Accel': 'Shift+Z, X',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'selected_objects_fixed_joint_mate_visibility_shower.svg'
            )
        }

    def Activated(self):
        import FreeCAD as App
        import traceback
        from logger import error

        from fixed_joint_mating import selected_objects_fixed_joint_mate_visibility_shower
        try:
            selected_objects_fixed_joint_mate_visibility_shower.run(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class SelectedObjectsFixedJointMateVisibilityHiderCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Mate LCS FixedJoints - visible hide (selected objects)',
            'ToolTip': 'Mate LCSes are made hidden. Applied to all FixedJoints within the selected objects.',
            'Accel': 'Shift+Z, C',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'selected_objects_fixed_joint_mate_visibility_hider.svg'
            )
        }

    def Activated(self):
        import FreeCAD as App
        import traceback
        from logger import error

        from fixed_joint_mating import selected_objects_fixed_joint_mate_visibility_hider
        try:
            selected_objects_fixed_joint_mate_visibility_hider.run(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class SelectedObjectsFixedJointMateVisibilityToggleCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Mate LCS FixedJoints - visible toggle (selected objects)',
            'ToolTip': 'Mate LCSes are made hidden. Applied to all FixedJoints within the selected objects.',
            'Accel': 'Shift+Z, V',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'selected_objects_fixed_joint_mate_visibility_toggler.svg'
            )
        }

    def Activated(self):
        import FreeCAD as App
        import traceback
        from logger import error

        from fixed_joint_mating import selected_objects_fixed_joint_mate_visibility_toggler
        try:
            selected_objects_fixed_joint_mate_visibility_toggler.run(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


COMMANDS = [
    SelectedObjectsFixedJointMaterCommand,
    SelectedObjectsFixedJointMateVisibilityShowerCommand,
    SelectedObjectsFixedJointMateVisibilityHiderCommand,
    SelectedObjectsFixedJointMateVisibilityToggleCommand
]

def register():
    for c in COMMANDS:
        FreeCADGui.addCommand(c.__name__, c())


def get_names():
    return [c.__name__ for c in COMMANDS]
