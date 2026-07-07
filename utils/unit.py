import FreeCAD as App


def get_default_unit():
    unit = App.Units.Quantity(1, App.Units.Length).getUserPreferred()[2]
    return unit

def as_default_unit(value: float):
    return App.Units.Quantity(f'1 {get_default_unit()}')

def one():
    return as_default_unit(1)
