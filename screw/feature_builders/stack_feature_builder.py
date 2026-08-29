import FreeCAD as App


def build_stack_feature(
        doc: App.Document,
        body: App.DocumentObject,
        child_bodies: list[App.DocumentObject]
):
    bottom = 0.0
    for child_body in child_bodies:
        doc.recompute([child_body])
        # print(f'{bottom=}')
        next_bottom = bottom + child_body.Shape.BoundBox.ZMax
        child_body.Placement = App.Placement(
            App.Vector(0, 0, bottom),
            App.Rotation(App.Vector(0, 0, 1), 0)
        )
        bottom = next_bottom
    boolean_fuse = body.newObject('PartDesign::Boolean', 'Screw fusion')
    boolean_fuse.addObjects(child_bodies)
    boolean_fuse.setObjects(child_bodies)
    boolean_fuse.Type = 0
    return boolean_fuse

