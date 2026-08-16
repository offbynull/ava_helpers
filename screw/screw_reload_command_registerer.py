import FreeCAD as App
import FreeCADGui


# WARNING: None of the imports outside are available, and __file__ isn't available either? That's why imports are
#          loaded internally.
class ScrewReloadCreatorCommand:
    def GetResources(self):
        from pathlib import Path
        return {
            'MenuText': 'Debug reload',
            'ToolTip': 'Reload module.',
            'Pixmap': str(
                Path(App.getUserAppDataDir())
                / 'Mod'
                / 'ava_helpers'
                / 'screw'
                / 'screw_reload.svg'
            )
        }

    def Activated(self):
        import sys
        import importlib

        package = 'screw'
        modules = [
            module
            for name, module in sys.modules.items()
            if name == package or name.startswith(package + ".")
        ]
        modules.sort(key=lambda m: m.__name__.count("."), reverse=True)  # Reload deepest modules first
        modules = [m for m in modules if 'screw_debug_reload' not in m.__name__]

        for module in modules:
            try:
                importlib.reload(module)
                print("Reloaded:", module.__name__)
            except Exception as e:
                print("FAILED:", module.__name__, e)

        print("Workbench modules reloaded")

    def IsActive(self):
        return True


COMMANDS = [
    ScrewReloadCreatorCommand,
]


def register():
    for c in COMMANDS:
        FreeCADGui.addCommand(c.__name__, c())


def get_names():
    return [c.__name__ for c in COMMANDS]
