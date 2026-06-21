import FreeCADGui as Gui
import FreeCAD as App


def get_all_descendants_under_selected_objects(doc: App.Document | None = None) -> list[App.DocumentObject]:
    roots = [o for o in Gui.Selection.getSelection() if o.Document is doc]
    seen = set()
    ret = []

    def add(o):
        if o.Name in seen:
            return
        seen.add(o.Name)
        ret.append(o)
        for c in getattr(o, "OutList", []):
            add(c)

    for r in roots:
        add(r)
    return ret

def get_all_descendants_under_active_object(doc: App.Document | None = None) -> list[App.DocumentObject]:
    doc = doc or App.ActiveDocument
    root = doc.ActiveObject
    if root is None:
        return []

    seen = set()
    ret = []

    def add(o):
        if o.Name in seen:
            return
        seen.add(o.Name)
        ret.append(o)
        for c in getattr(o, "OutList", []):
            add(c)

    add(root)