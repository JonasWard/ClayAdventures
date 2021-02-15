import Rhino.Geometry as rg
import math
from copy import deepcopy as dc

# general management functions used in the clay brick slicer

def pointSetToNurbsCurve(pt_set, closed = False):

    nurbs_crv = rg.NurbsCurve.Create(closed, 3, pt_set)

    return nurbs_crv


def vectorAngle(vector):

    x = vector[0]
    y = vector[1]

    length = (x ** 2 + y ** 2) **.5

    x /= length
    y /= length

    if y > 0.0:

        return math.acos(x)

    else:

        return math.pi * 2.0 - math.acos(x)


def lineCurveIntersection(line, crv, int_type = 'distance', pos_neg = True):

    loc_scale_val = 1000.0
    loc_interval = rg.Interval(0, 1000)

    loc_line = dc(line)
    
    if not(pos_neg):
        # if pos_neg == False -> change direction

        loc_line.To = 2 * loc_line.From - loc_line.To

    start_pt = loc_line.From
    end_pt = loc_line.To

    t_vals = []

    if int_type == "distance":

        pt_distance = start_pt.DistanceTo(end_pt)

        # intersection events generation

        int_events = rg.Intersect.Intersection.CurveLine(crv, loc_line, .1, .1)
        pts = [int_event.PointB for int_event in int_events]

        pt_set = []
        t_vals = []

        for pt in pts:

            dis_to_start = pt.DistanceTo(start_pt)
            dis_to_end = pt.DistanceTo(end_pt)

            if (dis_to_start < pt_distance):

                if (dis_to_end > pt_distance):

                    # we are only interested in positive values

                    # pt_set.append(pt)
                    # t_vals.append(-dis_to_start)

                    pass

                else:
                    
                    pt_set.append(pt)
                    t_vals.append(dis_to_start)

            else:

                if (dis_to_end > dis_to_start):

                    # we are only interested in positive values

                    # pt_set.append(pt)
                    # t_vals.append(-dis_to_start)

                    pass

                else:

                    pt_set.append(pt)
                    t_vals.append(dis_to_start)

    elif int_type == "curve_curve":

        loc_line.To = loc_line.From + loc_scale_val * (loc_line.To - loc_line.From)
        loc_line = loc_line.ToNurbsCurve()

        loc_line.Domain = loc_interval

        int_events = rg.Intersect.Intersection.CurveCurve(crv, loc_line, .01, .01)

        pt_set = [int_event.PointB for int_event in int_events]
        t_vals = [int_event.ParameterB for int_event in int_events]

    else:

        # if no int_type is used, use the default rhino geometry type
        # int_type == "standard"

        int_events = rg.Intersect.Intersection.CurveLine(crv, loc_line, .01, .01)
        pts = [int_event.PointB for int_event in int_events]
        t_set = [int_event.ParameterB for int_event in int_events]

        pt_set = []
        t_vals = []

        for t_in, t_val in enumerate(t_set):

            if t_val < 0:

                pass

            else:
                
                pt_set.append(pts[t_in])
                t_vals.append(t_val)

    # sorting

    t_vals, pt_set = zip(*sorted(zip(t_vals, pt_set)))

    return pt_set


def rhinoGeometryObjectType(base_object, types = None):

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


def placingInPlace(geometry, pt = None, z_val = 0.0):

    # if there is a give point or z_val

    extra_x, extra_y, extra_z = 0,0,0

    if not(pt == None):

        extra_vals = True
        extra_x, extra_y, extra_z = pt.X, pt.Y, pt.Z

    else:

        extra_vals = False

    if abs(z_val) > .0001:

        extra_vals = True
        extra_z = z_val

    # bounding box translation
    b_box = geometry.GetBoundingBox(rg.Plane.WorldXY)

    x_min, y_min, z_min = b_box.Min.X, b_box.Min.Y, b_box.Min.Z
    x_max, y_max, z_max = b_box.Max.X, b_box.Max.Y, b_box.Max.Z

    # when brep or mesh
    geom_object_height = z_max - z_min

    # center point of the lowest point of the structure
    if extra_vals:

        c_pt = rg.Point3d(
            extra_x - (x_min + x_max) * .5 , 
            extra_y - (y_min + y_max) * .5, 
            extra_z - z_min 
        )

    else:

        c_pt = rg.Point3d(
            - (x_min + x_max) * .5, 
            - (y_min + y_max) * .5, 
            - z_min
        )

    # translating the point to the origin
    geometry.Transform(rg.Transform.Translation(rg.Vector3d(c_pt)))

    return geom_object_height


def interpolatePts(pt_0, pt_1, val):

    pt_n = pt_1 - pt_0

    distance = pt_0.DistanceTo(pt_1)

    return pt_0 + pt_n * (val / distance)


def collapsePolylinePts(pt_set, value = 1.0):

    new_pt_set = [pt_set[0]]

    previous_pt = pt_set[0]
    final_pt = pt_set[-1]

    # for low for all the points except the last one

    for pt in pt_set[1:-1]:

        if previous_pt.DistanceTo(pt) > value:

            new_pt_set.append(rg.Point3d(pt))
            previous_pt = rg.Point3d(pt)

    i = -1

    while new_pt_set[i].DistanceTo(final_pt) < value:

        i -= 1

    new_pt_set = new_pt_set[:i] + [final_pt]

    return new_pt_set


def polylineSetPtsAtLength(pts, val):

    index_max = len(pts) - 2
    index = 0

    reached_val = False
    found_pts = False

    length = 0

    while not(reached_val):

        # print(index, index_max)

        pt_0 = pts[index]
        pt_1 = pts[index + 1]

        local_length = pt_0.DistanceTo(pt_1)

        if index == index_max:

            reached_val = True

        elif length + local_length > val:

            reached_val = True
            found_pts = True

        else:
            
            length += local_length

            index += 1

    if found_pts:

        n_pt = interpolatePts(pt_0, pt_1, val - length)

        new_list = [n_pt] + pts[index + 1:]

        return new_list

    else:

        return 0


def shortenPolylineSet(pt_set, value = 10.0, location = "end"):

    if location == "start":

        pt_set = polylineSetPtsAtLength(pt_set, value)

    elif location == "end":
        
        # print(pt_set)

        pt_set = pt_set[::-1]

        pt_set = polylineSetPtsAtLength(pt_set, value)

        pt_set = pt_set[::-1]

    elif location == "both":

        pt_set = shortenPolylineSet(pt_set, value = value, location = "start")
        pt_set = shortenPolylineSet(pt_set, value = value, location = "end")

    return pt_set


def crvOrienter(crv):

    x_or_y = True
    rot_angle = 0.0
    area = 9999999

    for i in range(90):

        angle = math.pi * i / 180

        # bounding box translation
        x_vec = rg.Vector3d(math.cos(angle), math.sin(angle), 0.0)
        y_vec = rg.Vector3d(- math.sin(angle), math.cos(angle), 0.0)
        b_box = crv.GetBoundingBox(rg.Plane(rg.Point3d(0,0,0), x_vec, y_vec))

        x_delta = b_box.Max.X - b_box.Min.X
        y_delta = b_box.Max.Y - b_box.Min.Y

        loc_are = x_delta * y_delta

        if loc_are < area:

            rot_angle = angle

            area = loc_are

            if x_delta < y_delta:

                x_or_y = False

            else:

                x_or_y = True

    if x_or_y:

        line = rg.Line(rg.Point3d(-1, 0, 0), rg.Point3d(1, 0, 0))

    else:

        line = rg.Line(rg.Point3d(0, -1, 0), rg.Point3d(0, 1, 0))

    line.Transform(rg.Transform.Rotation(rot_angle, rg.Point3d(0,0,0)))

    return line


def moveToSameHeight(ref_object, mv_object):

    z_ref = ref_object.PointAt(ref_object.Domain[0]).Z
    z_mv_obj = mv_object.PointAt(ref_object.Domain[0]).Z

    mv_vec = rg.Vector3d(0 ,0 , z_ref - z_mv_obj)
    mv = rg.Transform.Translation(mv_vec)

    output_obj = dc(mv_object)
    output_obj.Transform(mv)

    return output_obj


def crvIntersector(crv, other_object):

    obj_type = rhinoGeometryObjectType(other_object)

    if obj_type == 'line':

        tmp_other_obj = moveToSameHeight(crv, other_object)

        int_events = rg.Intersect.Intersection.CurveLine(crv, tmp_other_obj, .01, .01)

        pts = [int_event.PointA for int_event in int_events]
        t_vals = [int_event.ParameterA for int_event in int_events]

    elif obj_type == 'crv':

        tmp_other_obj = moveToSameHeight(crv, other_object)

        int_events = rg.Intersect.Intersection.CurveCurve(crv, tmp_other_obj, .01, .01)

        pts = [int_event.PointA for int_event in int_events]
        t_vals = [int_event.ParameterA for int_event in int_events]

    elif obj_type == 'plane':

        int_events = rg.Intersect.Intersection.CurvePlane(crv, other_object, .01)

        pts = [int_event.PointA for int_event in int_events]
        t_vals = [int_event.ParameterA for int_event in int_events]

    elif obj_type == 'brep':

        _, t_vals = rg.Intersect.Intersection.CurveBrep(crv, other_object, .01, .001)

        pts = [crv.PointAt(t_val) for t_val in t_vals]

    elif obj_type == 'num':

        crv.Domain = rg.Interval(0.0, 1.0)

        crv_length = crv.GetLength()
        length_0, length_1 = crv_length * obj_type, (1 - crv_length) * obj_type

        t_0, t_1 = crv.DivideByLength(length_0)[0], crv.DivideByLength(length_1)[0]

        t_vals = [t_0, t_1]

        pts = [crv.PointAt(t_val) for t_val in t_vals]

    else:

        print("object type %s is not supported" % obj_type)

        pts = []
        t_vals = []

    return pts, t_vals


def closestPointOnCurve(crv, pt):

    t_val = crv.ClosestPoint(pt)[1]

    output_pt = crv.PointAt(t_val)

    distance = output_pt.DistanceTo(pt)

    return output_pt, distance, t_val
    

def layer2ptIntersect(contour_crv, pts):

    if len(pts) == 2:

        pt_a, pt_b = pts[0], pts[1]

        # print("pt_a : ", pt_a, "pt_b : ", pt_b)

        pt_a, _, t_val = closestPointOnCurve(contour_crv, pt_a)

        contour_crv.ChangeClosedCurveSeam(t_val)
        contour_crv.Domain = rg.Interval(0.0, 1.0)

        pt_b, _, t_split = closestPointOnCurve(contour_crv, pt_b)

        result_crvs = contour_crv.Split(t_split)

        return result_crvs, [pt_a, pt_b]

    else:

        # print("you are dealing with %s" % len(pts))

        _, _, t_val = closestPointOnCurve(contour_crv, pts[0])

        contour_crv.ChangeClosedCurveSeam(t_val)
        contour_crv.Domain = rg.Interval(0.0, 1.0)

        t_split_set = [closestPointOnCurve(contour_crv, pt)[2] for pt in pts[1:]]

        t_split_set.sort()

        t_split_set = [0.0] + t_split_set

        result_crvs = contour_crv.Split(t_split_set)
        pt_set = [pts[0]] + [contour_crv.PointAt(t_val) for t_val in t_split_set]

        return result_crvs, pt_set


def rotObject90Degree(rot_object, rot_pt = None, other_angle = None):

    if rot_pt == None:

        types = [
            ('point', ['Vector3d', 'Point3d']),
            ('line',  ['Line'])
        ]

        obj_type = rhinoGeometryObjectType(rot_object, types = types)

        if obj_type == 'line':

            rot_pt = (rot_object.To + rot_object.From) * .5

        elif obj_type == 'point':

            rot_pt = rg.Point3d(0,0,0)

        else:

            print(" I don't know what to do with a %s object" % type(rot_object))

    if other_angle == None:

        angle = math.pi * .5

    else:

        angle = other_angle

    rot90 = rg.Transform.Rotation(angle, rot_pt)
    
    new_obj = dc(rot_object)
    new_obj.Transform(rot90)

    return new_obj

def longestCurve(crv_set, longest = True):

    length_set = [crv.GetLength() for crv in crv_set]

    _, crvs = zip(*sorted(zip(length_set, crv_set)))

    if longest:

        return crvs[-1]

    else:

        return crvs[0]


def extremePtsOfAxis(pts, split_axis):

    pts_on_axis = [split_axis.PointAt(split_axis.ClosestPoint(pt, 1000)[1]) for pt in pts]

    pt_differences = [(pt - pts_on_axis[i]) for i, pt in enumerate(pts)]

    vals = [(pt.X * abs(pt.X) + pt.Y * abs(pt.Y)) for pt in pt_differences]

    vals, pts = zip(*sorted(zip(vals, pts)))
    
    return [pts[0], pts[-1]]


def polylinePeriodicizer(crv, collapse_distance = 1.0):

    if not crv.IsClosed:

        print("I have to be closed")

        if crv.First.DistanceTo(crv.Last) < collapse_distance:

            print("& I have to collapse onto myself")

            crv.RemoveAt(crv.Count - 1)
        
        crv.Add(crv.First.X, crv.First.Y, crv.First.Z)

    return crv


def offsetLineSet(line, distance, direction = "inside", count = 2):

    if direction == "inside":

        direction = -1

    elif direction == "outside":

        direction = 1

    start_pt, end_pt = line.From, line.To
    c_pt =  ( start_pt + end_pt ) * .5

    y_vec = rg.Vector3d(end_pt - start_pt)
    y_vec.Unitize()
    y_vec = rotObject90Degree(y_vec)

    mv_vec_0 = rg.Vector3d(-c_pt.X, -c_pt.Y, 0) - y_vec * distance * (count - 1) * .5
    mv_vec = rg.Vector3d(y_vec * distance)
    
    mv_0 = rg.Transform.Translation(mv_vec_0)
    mv = rg.Transform.Translation(mv_vec)

    lines = []

    tmp_line = dc(line)
    tmp_line.Transform(mv_0)

    lines = [dc(tmp_line)]

    for i in range(count - 1):

        tmp_line.Transform(mv)

        lines.append(dc(tmp_line))

    return lines


def divideCurveInSegments(crv, seg_count):

    t_vals = crv.DivideByCount(seg_count, True)

    pts = [crv.PointAt(t) for t in t_vals]

    return pts

def divideCurveByLength(crv, length):

    print(crv)

    crv_l = crv.GetLength()

    div_c = int(crv_l / length)

    return divideCurveInSegments(crv, div_c)


def curveToPolyline(crv):

    types = [
        ('nurbscurve', ['NurbsCurve']),
        ('polylinecurve', ['PolylineCurve']),
        ('polyline', ['Polyline'])
    ]

    crv_type = rhinoGeometryObjectType(crv, types = types)

    if crv_type == 'nurbscurve':

        print(" I am a nurbs curve")

        loc_crv = rg.Polyline(divideCurveByLength(crv, 2.5))
    
    elif crv_type == 'polylinecurve':

        print(" I am a polyline curve")

        loc_crv = crv.ToPolyline()

    elif crv_type == 'polyline':

        print(" I am a polyline")

        loc_crv = crv

    return loc_crv

def polylineTypesToCurve(crv):

    types = [
            ('polycurve', ['PolyCurve']), 
            ('nurbscurve', ['NurbsCurve']),
            ('polylinecurve', ['PolylineCurve']),
            ('polyline', ['Polyline'])
        ]

    crv_type = rhinoGeometryObjectType(crv, types)
    # print(type(crv), crv_type)

    new_crv = crv

    if crv_type == 'polyline':

        # print("I am a polyline and I need to be turned into a curve!")

        new_crv = crv.ToPolylineCurve()
        new_crv.Domain = rg.Interval(0.0,1.0)

    elif crv_type == 'polylinecurve':

        new_crv.Domain = rg.Interval(0.0,1.0)

    elif crv_type == 'nurbscurve':

        new_crv = crv.ToPolyline(.01, 0.002, 0.1, 1000)
        new_crv.Domain = rg.Interval(0.0,1.0)

    elif crv_type == 'polycurve':

        new_crv = crv.ToPolyline(.01, 0.002, 0.1, 1000)
        new_crv.Domain = rg.Interval(0.0,1.0)

    else:

        print("you have a problematic curve on your hands!")
        print(type(crv))

    return new_crv

def curveRotator(crv):

    pln = rg.Plane(crv.PointAt(0.0), rg.Vector3d(0,0,1))

    tmp_offset_crv_1 = crv.Offset(pln, 1.0, .01, rg.CurveOffsetCornerStyle.Round)[0]
    tmp_offset_crv_2 = crv.Offset(pln, -1.0, .01, rg.CurveOffsetCornerStyle.Round)[0]

    if tmp_offset_crv_1.GetLength() < tmp_offset_crv_2.GetLength():

        crv.Reverse()

    return crv


def offsetCurveSet(crv, distance, direction = "inside", count = 2):

    pln = rg.Plane(crv.PointAt(0.0), rg.Vector3d(0,0,1))

    if direction == "inside":

        direction = -1

    elif direction == "outside":

        direction = 1

    crv = curveRotator(crv)

    distance *= direction

    # crv.Domain = rg.Interval(0.0, 1.0)

    loc_crv = curveToPolyline(crv)

    output_set = [polylinePeriodicizer(loc_crv)]

    if count > 1:

        o_type = rg.CurveOffsetCornerStyle.Sharp

        for i in range(1, count, 1):

            local_distance = i * distance

            offset_crv = crv.Offset(pln, local_distance, .01, o_type)[0]
            offset_crv = offset_crv.ToPolyline()

            offset_crv = polylinePeriodicizer(offset_crv)

            output_set.append(offset_crv)

    return output_set
