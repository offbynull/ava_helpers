import FreeCAD as App

_ORANGE = (1.0, 0.647, 0.0)
_PURPLE  = (0.5, 0.0, 0.5)


#def _set_pickable(obj, value):
#    # obj.ViewObject.Selectable = value
#    fn = getattr(obj.ViewObject, 'setPickable', None)
#    if fn:
#        try:
#            fn(value)
#            return
#        except Exception:
#            pass


def run(doc: App.Document, name='MaterLCS') -> App.DocumentObject:
    lcs = doc.addObject('Part::LocalCoordinateSystem', name)
    lcs.Label = name
    lcs.Visibility = True

    doc.recompute()

    for child in list(lcs.OriginFeatures):
        role = getattr(child, 'Role', '') or child.Name or child.Label
        print(role)
        assert role

        if role in {'Y_Axis', 'Y-Axis'}:
            child.Label = 'up'
            child.Visibility = True
            #child.ViewObject.LineColor = _ORANGE
            child.ViewObject.ShapeColor = _ORANGE
            child.ViewObject.ShowInTree = False
            # _set_pickable(child, False)  # Not respected, so don't bother
        elif role in {'Z_Axis', 'Z-Axis'}:
            child.Label = 'kiss'
            child.Visibility = True
            #child.ViewObject.LineColor = _PURPLE
            child.ViewObject.ShapeColor = _PURPLE
            child.ViewObject.ShowInTree = False
            # _set_pickable(child, False)  # Not respected, so don't bother
        else:
            child.Visibility = False
            child.ViewObject.ShowInTree = False
            # _set_pickable(child, False)  # Not respected, so don't bother

    lcs.Visibility = True
    # _set_pickable(lcs, True)  # Not respected, so don't bother

    return lcs
