from dataclasses import dataclass

import FreeCAD as App


def is_group(obj):
    return obj.TypeId.startswith('App::DocumentObjectGroup')

def tree_children(objs, obj):
    return [c for c in obj.ViewObject.claimChildren() if c in objs]

def find_roots(doc: App.Document, objs):
    claimed = set()
    for obj in objs:
        claimed.update(tree_children(objs, obj))
    return [o for o in objs if o not in claimed]


@dataclass
class Selectable:
    document_name: str
    root_name: str
    root_label: str
    sub_path: str
    sub_leaf_label: str

    def to_selection_tuple(self):
        return self.document_name, self.root_name, self.sub_path

    def to_friendly_string(self):
        return f'Root_label: {self.root_label} Object_label: {self.sub_leaf_label} -> {self.to_selection_tuple()}'

    @staticmethod
    def create(doc: App.Document, path):
        # remove Std_Group objects from selection path
        path = [o for o in path if not is_group(o)]

        if not path:
            return None

        root = path[0]
        sub = '.'.join(o.Name for o in path[1:])

        if sub:
            sub += '.'

        return Selectable(doc.Name, root.Name, root.Label, sub, path[-1].Label)

def walk(doc: App.Document, objs, obj, path=None, seen=None) -> list[Selectable]:
    path = [] if path is None else path
    seen = set() if seen is None else seen

    if obj in seen:
        return []

    seen.add(obj)

    try:
        path = path + [obj]
        ret = []

        sel = Selectable.create(doc, path)
        if sel:
            ret.append(sel)

        for child in tree_children(objs, obj):
            ret += walk(doc, objs, child, path, seen)

        return ret
    finally:
        seen.remove(obj)

def run(doc: App.Document):
    objs = set(doc.Objects)
    ret = []
    for root in find_roots(doc, objs):
        ret += walk(doc, objs, root)
    return ret