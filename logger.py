from typing import Any

import FreeCAD as App


def log(text: Any) -> None:
    App.Console.PrintMessage(str(text) + "\n")

def warn(text: Any) -> None:
    App.Console.PrintWarning(str(text) + "\n")

def error(text: Any) -> None:
    App.Console.PrintWarning(str(text) + "\n")