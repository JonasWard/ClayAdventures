# clay printing library - pin connection set

import Rhino.Geometry as rg
# import ghpythonlib.components as gh
# import math
from generalFunctions import *
# from simpleStartStop import *
from copy import deepcopy as dc

def lineInterpolate(pt_0, pt_2, count):

    delta_pt = (pt_2 - pt_0) / float(count + 1.0)

    return [pt_0 + delta_pt * i for i in range(1, count + 1, 1)]


def linkGen(pt_a, pt_b):

    distance = pt_a.DistanceTo(pt_b)
    
    end_pt = rg.Point3d((pt_b - pt_a) / distance + pt_a)
    
    return rg.Line(pt_a, end_pt), end_pt


def doubleEnd(pt, ref_line, alfa = .5):

    angle = alfa * 3.1415927

    rot_pos = rg.Transform.Rotation(angle, pt)
    rot_neg = rg.Transform.Rotation(-angle, pt)

    loc_copy_pos = dc(ref_line)
    loc_copy_neg = dc(ref_line)

    loc_copy_pos.Transform(rot_pos)
    loc_copy_neg.Transform(rot_neg)

    return loc_copy_pos, loc_copy_neg

def singleEnd(pt, ref_line, angle = 3.1415927):

    line = dc(ref_line)

    rot = rg.Transform.Rotation(angle, pt)

    line.Transform(rot)

    return line

def copyTransformSet(geo_set, trans_matrix):

    new_set = []

    for geo in geo_set:

        tmp_geo = dc(geo)
        tmp_geo.Transform(trans_matrix)

        new_set.append(tmp_geo)

    return new_set

def circleSegmenter(pt, pt_0, pt_1, items = 1, cutoff = .25):

    _, pt_0 = linkGen(pt, pt_0)
    _, pt_1 = linkGen(pt, pt_1)

    circle = rg.Circle(pt, 1.0).ToNurbsCurve()

    crvs, _ = layer2ptIntersect(circle, [pt_0, pt_1])
    crv_0 = crvs[0]
    crv_1 = crvs[1]

    crv_0_l = crv_0.GetLength()
    crv_1_l = crv_1.GetLength()

    if items == 1:

        if crv_0_l > crv_1_l :

            crv_0.Domain = rg.Interval(0,1)
            pt_2 = crv_0.PointAt(.5)

        else:

            crv_1.Domain = rg.Interval(0,1)
            pt_2 = crv_1.PointAt(.5)

        line_set = [rg.Line(pt, pt_2)]

        return [pt_2], line_set

    elif items == 2:

        crv_0.Domain = rg.Interval(0,1)
        pt_2 = crv_0.PointAt(.5)

        crv_1.Domain = rg.Interval(0,1)
        pt_3 = crv_1.PointAt(.5)

        line_set = [rg.Line(pt, pt_2), rg.Line(pt, pt_3)]

        return [pt_2, pt_3], line_set

    else:

        if max(crv_0_l, crv_1_l) < 3.1415927 + cutoff:
            # as if there are only two

            crv_0.Domain = rg.Interval(0,1)
            pt_2 = crv_0.PointAt(.5)

            crv_1.Domain = rg.Interval(0,1)
            pt_3 = crv_1.PointAt(.5)

            line_set = [rg.Line(pt, pt_2), rg.Line(pt, pt_3)]

            return [pt_2, pt_3], line_set

        else:

            if crv_0_l < crv_1_l:

                double_split_crv = crv_1
                double_crv_l = crv_1_l
                single_split_crv = crv_0
            
            else:

                double_split_crv = crv_0
                double_crv_l = crv_0_l
                single_split_crv = crv_1

            double_split_crv.Domain = rg.Interval(0,double_crv_l)
            single_split_crv.Domain = rg.Interval(0,1.0)
            
            pt_2 = single_split_crv.PointAt(.5)
            
            pt_3 = double_split_crv.PointAt(.5 * 3.1415927)
            pt_4 = double_split_crv.PointAt(double_crv_l - .5 * 3.1415927)

            line_set = [rg.Line(pt, pt_2), rg.Line(pt, pt_3), rg.Line(pt, pt_4)]

            return [pt_2, pt_3, pt_4], line_set

        
def createPinLinks(pin_points, connection_count = 2, max_main_line = 100.0, alfa = .5):

    pt_count = len(pin_points)

    main_lines = []
    secundary_lines = []

    # generating the main lines & potential too long ones

    main_link_pts = []

    for i in range(pt_count - 1):
        
        pt_0, pt_1 = pin_points[i], pin_points[i + 1]
        
        main_link_line, main_link_pt = linkGen(pt_0, pt_1)

        main_link_pts.append(main_link_pt)
        
        main_lines.append(dc(main_link_line))

        distance = pt_0.DistanceTo(pt_1)

        if distance > max_main_line:

            # indicating that some extra links should be introduced

            loc_link_set = doubleEnd(pt_0, main_link_line)

            split_count = int(round(distance / max_main_line))

            b_pts = lineInterpolate(pt_0, pt_1, split_count)

            for b_pt in b_pts:

                trans_m = rg.Transform.Translation(rg.Vector3d(b_pt - pt_0))

                secundary_lines.extend(copyTransformSet(loc_link_set, trans_m))

    # generating the main link end pts

    main_link_pts = main_link_pts + [pin_points[-1] + main_link_pts[-1]]

    # generating the "negative" pin links - "end parts"

    neg_main_pin_pts = []

    for i in range(pt_count - 1):
        
        pt_0, pt_1 = pin_points[i + 1], pin_points[i]
        
        _, neg_main_link_pt = linkGen(pt_0, pt_1)
        
        neg_main_pin_pts.append(neg_main_link_pt)

    neg_main_pin_pts = [pin_points[0] + neg_main_pin_pts[0]] + neg_main_pin_pts

    print("main link length: %s" %len(main_link_pts))

    # generating the point connection_lines

    pin_point_pt_set = [[main_link_pts[i], neg_main_pin_pts[i]] for i in range(pt_count)]

    if connection_count == 1:

        for pt_i, pt in enumerate(pin_points):

            if pt_i == 0:

                tmp_line = singleEnd(pt, main_lines[0])

                secundary_lines.append(tmp_line)

                pin_point_pt_set[0].extend([
                    tmp_line.PointAt(1.0)
                ])

            elif pt_i == (pt_count - 1):

                mv = rg.Transform.Translation(pt - pin_points[-2])

                tmp_line = copyTransformSet([main_lines[-1]], mv)[0]

                secundary_lines.append(tmp_line)

                pin_point_pt_set[-1].extend([
                    tmp_line.PointAt(1.0),
                ])

            else:

                pt_0 = pin_point_pt_set[pt_i][0]
                pt_1 = pin_point_pt_set[pt_i][1]

                pts, lines = circleSegmenter(pt, pt_0, pt_1, items = 1, cutoff = .25)
        
                secundary_lines.extend(lines)

                pin_point_pt_set[pt_i].extend(pts)

    elif connection_count == 3:

        for pt_i, pt in enumerate(pin_points):

            if pt_i == 0:

                tmp_line = singleEnd(pt, main_lines[0])
                tmp_lines = doubleEnd(pt, tmp_line)

                x_ls = list(tmp_lines)

                secundary_lines.extend(x_ls)

                pt_set = [l.PointAt(1.0) for l in x_ls]

                pin_point_pt_set[0].extend([l.PointAt(1.0) for l in x_ls])

            elif pt_i == (pt_count - 1):

                mv = rg.Transform.Translation(pt - pin_points[-2])

                tmp_line = copyTransformSet([main_lines[-1]], mv)[0]
                tmp_lines = doubleEnd(pt, tmp_line)

                x_ls = list(tmp_lines)

                secundary_lines.extend(x_ls)

                pt_set = [l.PointAt(1.0) for l in x_ls]

                pin_point_pt_set[-1].extend(pt_set)

            else:

                pt_0 = pin_point_pt_set[pt_i][0]
                pt_1 = pin_point_pt_set[pt_i][1]

                pts, lines = circleSegmenter(pt, pt_0, pt_1, items = 3, cutoff = alfa)
        
                secundary_lines.extend(lines)

                pin_point_pt_set[pt_i].extend(pts)

        pass

    else:

        for pt_i, pt in enumerate(pin_points):

            if pt_i == 0:

                tmp_lines = doubleEnd(pt, main_lines[0])

                x_ls = tmp_lines

                secundary_lines.extend(x_ls)

                pt_set = [l.PointAt(1.0) for l in x_ls]

                pin_point_pt_set[0].extend([l.PointAt(1.0) for l in x_ls])

            elif pt_i == (pt_count - 1):

                mv = rg.Transform.Translation(pt - pin_points[-2])

                tmp_line = copyTransformSet([main_lines[-1]], mv)[0]
                tmp_lines = doubleEnd(pt, tmp_line)

                x_ls = tmp_lines

                secundary_lines.extend(x_ls)

                pt_set = [l.PointAt(1.0) for l in x_ls] + [linkGen(pt, pin_points[-2])[1]]

                pin_point_pt_set[-1].extend(pt_set)

            else:

                pt_0 = pin_point_pt_set[pt_i][0]
                pt_1 = pin_point_pt_set[pt_i][1]

                pts, lines = circleSegmenter(pt, pt_0, pt_1, items = 2, cutoff = alfa)
        
                secundary_lines.extend(lines)

                pin_point_pt_set[pt_i].extend(pts)

    return pin_point_pt_set, secundary_lines, main_lines


def longestSegment(pin_point, pin_pt_set):

    c = rg.Circle(pin_point, 1.0).ToNurbsCurve()

    crvs, pts = layer2ptIntersect(c, pin_pt_set)

    longest_crv_length = 0.0

    for crv in crvs:

        loc_crv_length = crv.GetLength()

        if loc_crv_length > longest_crv_length:

            print(longest_crv_length)

            longest_crv_length = loc_crv_length
            longest_crv = crv

    longest_crv.Domain = rg.Interval(0, 1.0)
    longest_mid_pt = longest_crv.PointAt(.5)

    split_line = rg.Line(pin_point, longest_mid_pt)

    return split_line


def mainLinkGeneration(pin_main_crvs, main_lines):

    pass