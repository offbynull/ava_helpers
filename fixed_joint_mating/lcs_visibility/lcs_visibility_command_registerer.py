import FreeCAD as App
import FreeCADGui


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class MatePointVisibilityChangerCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Show/hide mate point',
            'ToolTip': 'Show/hide mater LCSes based on selection and regex.',
            'Accel': 'Shift+A, M, V, V',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'lcs_visibility'
                / 'lcs_visibility_changer.svg'
            )
        }

    def Activated(self):
        from logger import error
        import FreeCAD as App
        import traceback

        from fixed_joint_mating.lcs_visibility import lcs_visibility
        try:
            lcs_visibility.run_change(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class MatePointVisibilityShowerCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Show all mate points',
            'ToolTip': 'Show all mater LCSes.',
            'Accel': 'Shift+A, M, V, S',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'lcs_visibility'
                / 'lcs_visibility_shower.svg'
            )
        }

    def Activated(self):
        from logger import error
        import FreeCAD as App
        import traceback

        from fixed_joint_mating.lcs_visibility import lcs_visibility
        try:
            lcs_visibility.run_show_all(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True
    
    
# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class MatePointVisibilityHiderCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Hide all mate points',
            'ToolTip': 'Hide all mater LCSes.',
            'Accel': 'Shift+A, M, V, H',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'fixed_joint_mating'
                / 'lcs_visibility'
                / 'lcs_visibility_hider.svg'
            )
        }

    def Activated(self):
        from logger import error
        import FreeCAD as App
        import traceback

        from fixed_joint_mating.lcs_visibility import lcs_visibility
        try:
            lcs_visibility.run_hide_all(App.ActiveDocument)
        except Exception as exc:
            error(f'Failed: {exc}')
            error(traceback.format_exc())
            raise

    def IsActive(self):
        return True


COMMANDS = [
    MatePointVisibilityChangerCommand,
    MatePointVisibilityShowerCommand,
    MatePointVisibilityHiderCommand,
]

def register():
    for c in COMMANDS:
        FreeCADGui.addCommand(c.__name__, c())


def get_names():
    return [c.__name__ for c in COMMANDS]
