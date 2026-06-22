import FreeCAD as App
import FreeCADGui


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class DocumentFixedJointMaterCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Mate LCS FixedJoints (document)',
            'ToolTip': 'Reorients LCSes on a FixedJoint such that the z-axis kiss (point opposite each other) and the '
                       'y-axis point in the same direction. Applied to all FixedJoints within the document.',
            'Accel': 'Shift+Q,Q',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'document_fixed_joint_mater.svg'
            )
        }

    def Activated(self):
        import FreeCAD as App
        import traceback
        from logger import error

        from fixed_joint_mating import document_fixed_joint_mater
        try:
            document_fixed_joint_mater.run(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class DocumentFixedJointMateVisibilityShowerCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Mate LCS FixedJoints - visible true (document)',
            'ToolTip': 'Mate LCSes are made visible. Applied to all FixedJoints within the document.',
            'Accel': 'Shift+Q,W',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'document_fixed_joint_mate_visibility_shower.svg'
            )
        }

    def Activated(self):
        import FreeCAD as App
        import traceback
        from logger import error

        from fixed_joint_mating import document_fixed_joint_mate_visibility_shower
        try:
            document_fixed_joint_mate_visibility_shower.run(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class DocumentFixedJointMateVisibilityHiderCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Mate LCS FixedJoints - visible hide (document)',
            'ToolTip': 'Mate LCSes are made hidden. Applied to all FixedJoints within the document.',
            'Accel': 'Shift+Q,E',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'document_fixed_joint_mate_visibility_hider.svg'
            )
        }

    def Activated(self):
        import FreeCAD as App
        import traceback
        from logger import error

        from fixed_joint_mating import document_fixed_joint_mate_visibility_hider
        try:
            document_fixed_joint_mate_visibility_hider.run(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class DocumentFixedJointMateVisibilityToggleCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Mate LCS FixedJoints - visible toggle (document)',
            'ToolTip': 'Mate LCSes are made hidden. Applied to all FixedJoints within the document.',
            'Accel': 'Shift+Q,R',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'document_fixed_joint_mate_visibility_toggler.svg'
            )
        }

    def Activated(self):
        import FreeCAD as App
        import traceback
        from logger import error

        from fixed_joint_mating import document_fixed_joint_mate_visibility_toggler
        try:
            document_fixed_joint_mate_visibility_toggler.run(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


COMMANDS = [
    DocumentFixedJointMaterCommand,
    DocumentFixedJointMateVisibilityShowerCommand,
    DocumentFixedJointMateVisibilityHiderCommand,
    DocumentFixedJointMateVisibilityToggleCommand
]


def register():
    for c in COMMANDS:
        FreeCADGui.addCommand(c.__name__, c())


def get_names():
    return [c.__name__ for c in COMMANDS]
