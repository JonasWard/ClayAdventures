# geometry management
import Rhino.Geometry as rg

def getRhinoType(base_object, types = None):

    if types == None:

        types = [
            ('num', ['float', 'int']),
            ('point', ['Vector3d, Point3d']),
            ('plane', ['Plane']),
            ('line', ['Line']),
            ('crv', ['NurbsCurve', 'Curve', 'PolylineCurve', 'LineCurve', 'PolyCurve']),
            ('mesh', ['Mesh']),
            ('brep', ['Brep'])
        ]

    obj_type = "other"

    type_found = False

    for type_tuple in types:

        for type_val in type_tuple[1]:

            if (str(type(base_object)).find(type_val) > 0):

                obj_type = type_tuple[0]

                type_found = True

                break

        if type_found:

            break

    return obj_type

def crvToPolyline(crv):

def polylineToCrv(polyline):