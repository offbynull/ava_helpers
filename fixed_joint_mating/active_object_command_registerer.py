import FreeCAD as App
import FreeCADGui


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class ActiveObjectFixedJointMaterCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Mate LCS FixedJoints (active object)',
            'ToolTip': 'Reorients LCSes on a FixedJoint such that the z-axis kiss (point opposite each other) and the '
                       'y-axis point in the same direction. Applied to all FixedJoints within the active object.',
            'Accel': 'Shift+A,A',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'active_object_fixed_joint_mater.svg'
            )
        }

    def Activated(self):
        import FreeCAD as App
        import traceback
        from logger import error

        from fixed_joint_mating import active_object_fixed_joint_mater
        try:
            active_object_fixed_joint_mater.run(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class ActiveObjectFixedJointMateVisibilityShowerCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Mate LCS FixedJoints - visible show (active object)',
            'ToolTip': 'Mate LCSes are made visible. Applied to all FixedJoints within the active object.',
            'Accel': 'Shift+A,S',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'active_object_fixed_joint_mate_visibility_shower.svg'
            )
        }

    def Activated(self):
        import FreeCAD as App
        import traceback
        from logger import error

        from fixed_joint_mating import active_object_fixed_joint_mate_visibility_shower
        try:
            active_object_fixed_joint_mate_visibility_shower.run(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class ActiveObjectFixedJointMateVisibilityHiderCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Mate LCS FixedJoints - visible hide (active object)',
            'ToolTip': 'Mate LCSes are made hidden. Applied to all FixedJoints within the active object.',
            'Accel': 'Shift+A,D',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'active_object_fixed_joint_mate_visibility_hider.svg'
            )
        }

    def Activated(self):
        import FreeCAD as App
        import traceback
        from logger import error

        from fixed_joint_mating import active_object_fixed_joint_mate_visibility_hider
        try:
            active_object_fixed_joint_mate_visibility_hider.run(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class ActiveObjectFixedJointMateVisibilityToggleCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Mate LCS FixedJoints - visible toggle (active object)',
            'ToolTip': 'Mate LCSes are made hidden. Applied to all FixedJoints within the active object.',
            'Accel': 'Shift+A,F',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'active_object_fixed_joint_mate_visibility_toggler.svg'
            )
        }

    def Activated(self):
        import FreeCAD as App
        import traceback
        from logger import error

        from fixed_joint_mating import active_object_fixed_joint_mate_visibility_toggler
        try:
            active_object_fixed_joint_mate_visibility_toggler.run(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


COMMANDS = [
    ActiveObjectFixedJointMaterCommand,
    ActiveObjectFixedJointMateVisibilityShowerCommand,
    ActiveObjectFixedJointMateVisibilityHiderCommand,
    ActiveObjectFixedJointMateVisibilityToggleCommand
]

def register():
    for c in COMMANDS:
        FreeCADGui.addCommand(c.__name__, c())


def get_names():
    return [c.__name__ for c in COMMANDS]
