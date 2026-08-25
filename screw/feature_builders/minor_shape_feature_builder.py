import FreeCAD as App

from screw.geometries.cone_frustum import ConeFrustum
from screw.geometries.cylinder import Cylinder


def build_minor_cone_feature(
            doc: App.Document,
            body: App.DocumentObject,
            minor_shape: ConeFrustum | Cylinder
    ):
        return minor_shape.create_partdesign_additive_cone(body, 'Minor Cone')