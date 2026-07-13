import math

import FreeCAD as App
import Part
import Sketcher


def create_uneased_slab(
        doc: App.Document,
        name: str,
        label: str,
        retailer: str,
        retailer_part_numer: str,
        t: float,
        w: float,
        l: float
) -> App.DocumentObject:
    varset = doc.addObject('App::VarSet', f'{name}_Parameters')
    varset.Label = f'{label} Parameters'
    varset.addProperty('App::PropertyString', 'Retailer', 'Retail', 'Retailer')
    varset.Retailer = retailer
    varset.addProperty('App::PropertyString', 'RetailerPart', 'Retail', 'Retailer Part')
    varset.RetailerPart = retailer_part_numer
    varset.addProperty('App::PropertyLength', 'Length', 'Dimensions', 'Length')
    varset.Length = App.Units.Quantity(l, 'in')
    varset.addProperty('App::PropertyLength', 'Width', 'Dimensions', 'Width')
    varset.Width = App.Units.Quantity(w, 'in')
    varset.addProperty('App::PropertyLength', 'Thickness', 'Dimensions', 'Thickness')
    varset.Thickness = App.Units.Quantity(t, 'in')

    body = doc.addObject('PartDesign::Body', name)
    body.Label = label
    body.addProperty('App::PropertyString', 'Retailer', 'Retail', 'Retailer')
    body.setEditorMode('Retailer', 1)
    body.addProperty('App::PropertyString', 'RetailerPart', 'Retail', 'Retailer Part')
    body.setEditorMode('RetailerPart', 1)
    body.addProperty('App::PropertyLength', 'Length', 'Dimensions', 'Length')
    body.setEditorMode('Length', 1)
    body.addProperty('App::PropertyLength', 'Width', 'Dimensions', 'Width')
    body.setEditorMode('Width', 1)
    body.addProperty('App::PropertyLength', 'Thickness', 'Dimensions', 'Thickness')
    body.setEditorMode('Thickness', 1)

    body.setExpression('Retailer', f'{varset.Name}.Retailer')
    body.setExpression('RetailerPart', f'{varset.Name}.RetailerPart')
    body.setExpression('Length', f'{varset.Name}.Length')
    body.setExpression('Width', f'{varset.Name}.Width')
    body.setExpression('Thickness', f'{varset.Name}.Thickness')

    box = body.newObject('PartDesign::AdditiveBox', 'AdditiveBox')
    box.setExpression('Length', f'{varset.Name}.Length')
    box.setExpression('Width', f'{varset.Name}.Width')
    box.setExpression('Height', f'{varset.Name}.Thickness')
    body.Tip = box

    group = doc.addObject('App::DocumentObjectGroup', f'{name}_Group')
    group.Label = f'{label} Group'
    group.addObject(varset)
    group.addObject(body)
    return group


def create_eased_slab(
        doc: App.Document,
        name: str,
        label: str,
        retailer: str,
        retailer_part_numer: str,
        t: float,
        w: float,
        l: float,
        r: float
) -> App.DocumentObject:
    varset = doc.addObject('App::VarSet', f'{name}_Parameters')
    varset.Label = f'{label} Parameters'
    varset.addProperty('App::PropertyString', 'Retailer', 'Retail', 'Retailer')
    varset.Retailer = retailer
    varset.addProperty('App::PropertyString', 'RetailerPart', 'Retail', 'Retailer Part')
    varset.RetailerPart = retailer_part_numer
    varset.addProperty('App::PropertyLength', 'Length', 'Dimensions', 'Length')
    varset.Length = App.Units.Quantity(l, 'in')
    varset.addProperty('App::PropertyLength', 'Width', 'Dimensions', 'Width')
    varset.Width = App.Units.Quantity(w, 'in')
    varset.addProperty('App::PropertyLength', 'Thickness', 'Dimensions', 'Thickness')
    varset.Thickness = App.Units.Quantity(t, 'in')
    varset.addProperty('App::PropertyLength', 'EasingRadius', 'Dimensions', 'Easing Radius')
    varset.EasingRadius = App.Units.Quantity(r, 'in')

    body = doc.addObject('PartDesign::Body', name)
    body.Label = label
    body.addProperty('App::PropertyString', 'Retailer', 'Retail', 'Retailer')
    body.setEditorMode('Retailer', 1)
    body.addProperty('App::PropertyString', 'RetailerPart', 'Retail', 'Retailer Part')
    body.setEditorMode('RetailerPart', 1)
    body.addProperty('App::PropertyLength', 'Length', 'Dimensions', 'Length')
    body.setEditorMode('Length', 1)
    body.addProperty('App::PropertyLength', 'Width', 'Dimensions', 'Width')
    body.setEditorMode('Width', 1)
    body.addProperty('App::PropertyLength', 'Thickness', 'Dimensions', 'Thickness')
    body.setEditorMode('Thickness', 1)
    body.addProperty('App::PropertyLength', 'EasingRadius', 'Dimensions', 'Easing Radius')
    body.setEditorMode('EasingRadius', 1)

    body.setExpression('Retailer', f'{varset.Name}.Retailer')
    body.setExpression('RetailerPart', f'{varset.Name}.RetailerPart')
    body.setExpression('Length', f'{varset.Name}.Length')
    body.setExpression('Width', f'{varset.Name}.Width')
    body.setExpression('Thickness', f'{varset.Name}.Thickness')
    body.setExpression('EasingRadius', f'{varset.Name}.EasingRadius')

    sketch = body.newObject('Sketcher::SketchObject', 'Sketch')
    sketch.AttachmentSupport = (
        next(obj for obj in body.Origin.OriginFeatures if obj.Name.startswith('YZ_Plane')),
        ['']
    )
    sketch.MapMode = 'FlatFace'
    tq = App.Units.Quantity(t, 'in').Value
    wq = App.Units.Quantity(w, 'in').Value
    rq = App.Units.Quantity(r, 'in').Value
    lq = App.Units.Quantity(l, 'in').Value
    x = tq / 2
    y = wq / 2
    sketch.addGeometry([
        Part.LineSegment(App.Vector(-x + rq, -y, 0), App.Vector(x - rq, -y, 0)),
        Part.LineSegment(App.Vector(x, -y + rq, 0), App.Vector(x, y - rq, 0)),
        Part.LineSegment(App.Vector(x - rq, y, 0), App.Vector(-x + rq, y, 0)),
        Part.LineSegment(App.Vector(-x, y - rq, 0), App.Vector(-x, -y + rq, 0)),
        Part.ArcOfCircle(Part.Circle(App.Vector(-x + rq, -y + rq, 0), App.Vector(0, 0, 1), rq), math.pi,
                         3 * math.pi / 2),
        Part.ArcOfCircle(Part.Circle(App.Vector(x - rq, -y + rq, 0), App.Vector(0, 0, 1), rq), 3 * math.pi / 2,
                         2 * math.pi),
        Part.ArcOfCircle(Part.Circle(App.Vector(x - rq, y - rq, 0), App.Vector(0, 0, 1), rq), 0, math.pi / 2),
        Part.ArcOfCircle(Part.Circle(App.Vector(-x + rq, y - rq, 0), App.Vector(0, 0, 1), rq), math.pi / 2, math.pi)
    ], False)
    sketch.addGeometry([
        Part.Point(App.Vector(x, y, 0)),
        Part.Point(App.Vector(0, 0, 0))
    ], True)
    sketch.addConstraint([
        Sketcher.Constraint('Tangent', 0, 1, 4, 2),
        Sketcher.Constraint('Tangent', 0, 2, 5, 1),
        Sketcher.Constraint('Tangent', 1, 1, 5, 2),
        Sketcher.Constraint('Tangent', 1, 2, 6, 1),
        Sketcher.Constraint('Tangent', 2, 1, 6, 2),
        Sketcher.Constraint('Tangent', 2, 2, 7, 1),
        Sketcher.Constraint('Tangent', 3, 1, 7, 2),
        Sketcher.Constraint('Tangent', 3, 2, 4, 1),
        Sketcher.Constraint('Horizontal', 0),
        Sketcher.Constraint('Horizontal', 2),
        Sketcher.Constraint('Vertical', 1),
        Sketcher.Constraint('Vertical', 3),
        Sketcher.Constraint('Equal', 4, 5),
        Sketcher.Constraint('Equal', 5, 6),
        Sketcher.Constraint('Equal', 6, 7),
        Sketcher.Constraint('Symmetric', 2, 1, 0, 1, 9, 1),
        Sketcher.Constraint('PointOnObject', 8, 1, 1),
        Sketcher.Constraint('PointOnObject', 8, 1, 2),
        Sketcher.Constraint('Coincident', 9, 1, -1, 1)
    ])
    thickness_constraint = sketch.addConstraint(
        Sketcher.Constraint('Distance', 1, 1, 3, 2, App.Units.Quantity(t, 'in')))
    sketch.renameConstraint(thickness_constraint, 'Thickness')
    sketch.setExpression('Constraints.Thickness', f'{varset.Name}.Thickness')
    width_constraint = sketch.addConstraint(
        Sketcher.Constraint('Distance', 0, 1, 2, 2, App.Units.Quantity(w, 'in')))
    sketch.renameConstraint(width_constraint, 'Width')
    sketch.setExpression('Constraints.Width', f'{varset.Name}.Width')
    radius_constraint = sketch.addConstraint(Sketcher.Constraint('Radius', 5, App.Units.Quantity(r, 'in')))
    sketch.renameConstraint(radius_constraint, 'EasingRadius')
    sketch.setExpression('Constraints.EasingRadius', f'{varset.Name}.EasingRadius')
    sketch.Visibility = False

    pad = body.newObject('PartDesign::Pad', 'Pad')
    pad.Profile = sketch
    pad.setExpression('Length', f'{varset.Name}.Length')

    wire_front = body.newObject('Sketcher::SketchObject', 'UneasedWireStart')
    wire_front.AttachmentSupport = (
        next(obj for obj in body.Origin.OriginFeatures if obj.Name.startswith('YZ_Plane')),
        ['']
    )
    wire_front.MapMode = 'FlatFace'
    wire_front.addGeometry([
        Part.LineSegment(App.Vector(-x, -y, 0), App.Vector(x, -y, 0)),
        Part.LineSegment(App.Vector(x, -y, 0), App.Vector(x, y, 0)),
        Part.LineSegment(App.Vector(x, y, 0), App.Vector(-x, y, 0)),
        Part.LineSegment(App.Vector(-x, y, 0), App.Vector(-x, -y, 0))
    ], False)
    wire_front.addConstraint([
        Sketcher.Constraint('Coincident', 0, 2, 1, 1),
        Sketcher.Constraint('Coincident', 1, 2, 2, 1),
        Sketcher.Constraint('Coincident', 2, 2, 3, 1),
        Sketcher.Constraint('Coincident', 3, 2, 0, 1),
        Sketcher.Constraint('Horizontal', 0),
        Sketcher.Constraint('Horizontal', 2),
        Sketcher.Constraint('Vertical', 1),
        Sketcher.Constraint('Vertical', 3),
        Sketcher.Constraint('Symmetric', 2, 1, 0, 1, -1, 1)
    ])
    thickness_constraint = wire_front.addConstraint(
        Sketcher.Constraint('Distance', 1, 1, 3, 2, App.Units.Quantity(t, 'in')))
    wire_front.renameConstraint(thickness_constraint, 'Thickness')
    wire_front.setExpression('Constraints.Thickness', f'{varset.Name}.Thickness')
    width_constraint = wire_front.addConstraint(
        Sketcher.Constraint('Distance', 0, 1, 2, 2, App.Units.Quantity(w, 'in')))
    wire_front.renameConstraint(width_constraint, 'Width')
    wire_front.setExpression('Constraints.Width', f'{varset.Name}.Width')

    wire_rear = body.newObject('Sketcher::SketchObject', 'UneasedWireEnd')
    wire_rear.AttachmentSupport = (
        next(obj for obj in body.Origin.OriginFeatures if obj.Name.startswith('YZ_Plane')),
        ['']
    )
    wire_rear.MapMode = 'FlatFace'
    wire_rear.AttachmentOffset = App.Placement(App.Vector(0, 0, App.Units.Quantity(l, 'in').Value), App.Rotation())
    wire_rear.setExpression('AttachmentOffset.Base.z', f'{varset.Name}.Length')
    wire_rear.addGeometry([
        Part.LineSegment(App.Vector(-x, -y, 0), App.Vector(x, -y, 0)),
        Part.LineSegment(App.Vector(x, -y, 0), App.Vector(x, y, 0)),
        Part.LineSegment(App.Vector(x, y, 0), App.Vector(-x, y, 0)),
        Part.LineSegment(App.Vector(-x, y, 0), App.Vector(-x, -y, 0))
    ], False)
    wire_rear.addConstraint([
        Sketcher.Constraint('Coincident', 0, 2, 1, 1),
        Sketcher.Constraint('Coincident', 1, 2, 2, 1),
        Sketcher.Constraint('Coincident', 2, 2, 3, 1),
        Sketcher.Constraint('Coincident', 3, 2, 0, 1),
        Sketcher.Constraint('Horizontal', 0),
        Sketcher.Constraint('Horizontal', 2),
        Sketcher.Constraint('Vertical', 1),
        Sketcher.Constraint('Vertical', 3),
        Sketcher.Constraint('Symmetric', 2, 1, 0, 1, -1, 1)
    ])
    thickness_constraint = wire_rear.addConstraint(
        Sketcher.Constraint('Distance', 1, 1, 3, 2, App.Units.Quantity(t, 'in')))
    wire_rear.renameConstraint(thickness_constraint, 'Thickness')
    wire_rear.setExpression('Constraints.Thickness', f'{varset.Name}.Thickness')
    width_constraint = wire_rear.addConstraint(
        Sketcher.Constraint('Distance', 0, 1, 2, 2, App.Units.Quantity(w, 'in')))
    wire_rear.renameConstraint(width_constraint, 'Width')
    wire_rear.setExpression('Constraints.Width', f'{varset.Name}.Width')

    wire_bottom = body.newObject('Sketcher::SketchObject', 'UneasedWireBottom')
    wire_bottom.AttachmentSupport = (
        next(obj for obj in body.Origin.OriginFeatures if obj.Name.startswith('XY_Plane')),
        ['']
    )
    wire_bottom.MapMode = 'FlatFace'
    wire_bottom.AttachmentOffset = App.Placement(App.Vector(0, 0, -y), App.Rotation())
    wire_bottom.setExpression('AttachmentOffset.Base.z', f'-{varset.Name}.Width / 2')
    wire_bottom.addGeometry([
        Part.LineSegment(App.Vector(0, -x, 0), App.Vector(lq, -x, 0)),
        Part.LineSegment(App.Vector(0, x, 0), App.Vector(lq, x, 0))
    ], False)
    wire_bottom.addConstraint([
        Sketcher.Constraint('Horizontal', 0),
        Sketcher.Constraint('Horizontal', 1),
        Sketcher.Constraint('DistanceY', 0, 1, 1, 1, App.Units.Quantity(t, 'in')),
        Sketcher.Constraint('DistanceX', 0, 1, 0, 2, App.Units.Quantity(l, 'in')),
        Sketcher.Constraint('DistanceX', 1, 1, 1, 2, App.Units.Quantity(l, 'in')),
        Sketcher.Constraint('PointOnObject', 0, 1, -2),
        Sketcher.Constraint('Symmetric', 0, 1, 1, 1, -1)
    ])
    wire_bottom.renameConstraint(2, 'Thickness')
    wire_bottom.setExpression('Constraints.Thickness', f'{varset.Name}.Thickness')
    wire_bottom.renameConstraint(3, 'LengthA')
    wire_bottom.setExpression('Constraints.LengthA', f'{varset.Name}.Length')
    wire_bottom.renameConstraint(4, 'LengthB')
    wire_bottom.setExpression('Constraints.LengthB', f'{varset.Name}.Length')

    wire_top = body.newObject('Sketcher::SketchObject', 'UneasedWireTop')
    wire_top.AttachmentSupport = (
        next(obj for obj in body.Origin.OriginFeatures if obj.Name.startswith('XY_Plane')),
        ['']
    )
    wire_top.MapMode = 'FlatFace'
    wire_top.AttachmentOffset = App.Placement(App.Vector(0, 0, y), App.Rotation())
    wire_top.setExpression('AttachmentOffset.Base.z', f'{varset.Name}.Width / 2')
    wire_top.addGeometry([
        Part.LineSegment(App.Vector(0, -x, 0), App.Vector(lq, -x, 0)),
        Part.LineSegment(App.Vector(0, x, 0), App.Vector(lq, x, 0))
    ], False)
    wire_top.addConstraint([
        Sketcher.Constraint('Horizontal', 0),
        Sketcher.Constraint('Horizontal', 1),
        Sketcher.Constraint('DistanceY', 0, 1, 1, 1, App.Units.Quantity(t, 'in')),
        Sketcher.Constraint('DistanceX', 0, 1, 0, 2, App.Units.Quantity(l, 'in')),
        Sketcher.Constraint('DistanceX', 1, 1, 1, 2, App.Units.Quantity(l, 'in')),
        Sketcher.Constraint('PointOnObject', 0, 1, -2),
        Sketcher.Constraint('Symmetric', 0, 1, 1, 1, -1)
    ])
    wire_top.renameConstraint(2, 'Thickness')
    wire_top.setExpression('Constraints.Thickness', f'{varset.Name}.Thickness')
    wire_top.renameConstraint(3, 'LengthA')
    wire_top.setExpression('Constraints.LengthA', f'{varset.Name}.Length')
    wire_top.renameConstraint(4, 'LengthB')
    wire_top.setExpression('Constraints.LengthB', f'{varset.Name}.Length')

    body.Tip = pad

    group = doc.addObject('App::DocumentObjectGroup', f'{name}_Group')
    group.Label = f'{label} Group'
    group.addObject(varset)
    group.addObject(body)
    return group