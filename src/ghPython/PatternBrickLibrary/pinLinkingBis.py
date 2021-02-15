# pin linking
import Rhino.Geometry as rg
from copy import deepcopy as dc
from generalFunctions import *
from brickSlicer import Pin
from layerFunctions import LineSet

def lineInterpolate(pt_0, pt_2, count):

    delta_pt = (pt_2 - pt_0) / float(count + 1.0)

    return [pt_0 + delta_pt * i for i in range(1, count + 1, 1)]


def linkGen(pt_a, pt_b):

    distance = pt_a.DistanceTo(pt_b)
    
    end_pt = rg.Point3d((pt_b - pt_a) / distance + pt_a)
    
    return rg.Line(pt_a, end_pt), end_pt


def copyTransformSet(geo_set, trans_matrix):

    new_set = []

    for geo in geo_set:

        tmp_geo = dc(geo)
        tmp_geo.Transform(trans_matrix)

        new_set.append(tmp_geo)

    return new_set


def startEnd(pt, pt_bis, count, alfa):

    pt_set = []
    link_lines = []

    if count > 1:

        alfa_delta = ( 6.2831853072 - 2 * alfa ) / (count - 1)

        for i in range(count):

            loc_angle = alfa + alfa_delta * i
            rot_m = rg.Transform.Rotation(loc_angle, pt)

            loc_pt = dc(pt_bis)
            loc_pt.Transform(rot_m)

            pt_set.append(loc_pt)
            link_lines.append(rg.Line(pt, loc_pt))

    elif count == 0:

        pass

    else:

        # case will consider count == 1

        loc_angle = 3.1415927
        rot_m = rg.Transform.Rotation(loc_angle, pt)

        loc_pt = dc(pt_bis)
        loc_pt.Transform(rot_m)

        pt_set.append(loc_pt)
        link_lines.append(rg.Line(pt, loc_pt))

    return link_lines, pt_set
    

def start(pt, pt_1, count, alfa = .5):

    # _, pt_a = linkGen(pt, pt_0)
    main_link, pt_b = linkGen(pt, pt_1)
    # main_link = rg.Line(pt, pt_1)

    link_lines, pt_set = startEnd(pt, pt_b, count, alfa)
    pt_set = [pt_b] + pt_set

    return main_link, link_lines, pt_set


def end(pt_0, pt, count, alfa = .5):

    _, pt_a = linkGen(pt, pt_0)
    # main_link, pt_b = linkGen(pt, pt_1)

    link_lines, pt_set = startEnd(pt, pt_a, count, alfa)
    pt_set = [pt_a] + pt_set

    main_link = None

    return main_link, link_lines, pt_set


def mid(pt_0, pt, pt_1, count, min_alfa = .25):

    _, pt_a = linkGen(pt, pt_0)
    main_link, pt_b = linkGen(pt, pt_1)
    # main_link = rg.Line(pt, pt_1)

    link_lines, pt_set = midDivide(pt_a, pt, pt_b, items=count, cutoff=min_alfa)

    pt_set = [pt_a, pt_b] + pt_set

    return main_link, link_lines, pt_set


def midDivide(pt_0, pt, pt_1, items = 1, cutoff = .25):

    _, pt_0 = linkGen(pt, pt_0)
    _, pt_1 = linkGen(pt, pt_1)

    circle = rg.Circle(pt, 1.0).ToNurbsCurve()

    crvs, _ = layer2ptIntersect(circle, [pt_0, pt_1])
    crv_0 = crvs[0]
    crv_1 = crvs[1]

    crv_0_l = crv_0.GetLength()
    crv_1_l = crv_1.GetLength()

    if crv_0_l < crv_1_l:

        double_split_crv = crv_1
        double_crv_l = crv_1_l
        single_split_crv = crv_0
    
    else:

        double_split_crv = crv_0
        double_crv_l = crv_0_l
        single_split_crv = crv_1

    if items < 2:

        double_split_crv.Domain = rg.Interval(0.0, 1.0)
        pt_2 = double_split_crv.PointAt(.5)

        line_set = [rg.Line(pt, pt_2)]

        pt_set = [pt_2]

    elif items == 2:

        single_split_crv.Domain = rg.Interval(0,1)
        pt_2 = single_split_crv.PointAt(.5)

        double_split_crv.Domain = rg.Interval(0,1)
        pt_3 = double_split_crv.PointAt(.5)

        line_set = [rg.Line(pt, pt_2), rg.Line(pt, pt_3)]

        pt_set = [pt_2, pt_3]

    else:

        if double_crv_l < 3.1415927 + cutoff:
            
            line_set, pt_set = midDivide(pt_0, pt, pt_1, items = 2)

        else:

            double_split_crv.Domain = rg.Interval(0,double_crv_l)
            single_split_crv.Domain = rg.Interval(0,1.0)
            
            pt_2 = single_split_crv.PointAt(.5)
            
            pt_3 = double_split_crv.PointAt(.5 * 3.1415927)
            pt_4 = double_split_crv.PointAt(double_crv_l - .5 * 3.1415927)

            line_set = [rg.Line(pt, pt_2), rg.Line(pt, pt_3), rg.Line(pt, pt_4)]

            pt_set = [pt_2, pt_3, pt_4]

    return line_set, pt_set


def longestSegment(pin_point, pin_pt_set, second_one = False):

    c = rg.Circle(pin_point, 1.0).ToNurbsCurve()

    crvs, pts = layer2ptIntersect(c, pin_pt_set)

    crv_lengths = [crv.GetLength() for crv in crvs]

    crv_lengths, crvs = zip(*sorted(zip(crv_lengths, crvs)))

    print("this is the list of crv lengths")
    print(crv_lengths)

    longest_crv = crvs[-1]
    second_longest_crv = crvs[-2]

    longest_crv.Domain = rg.Interval(0, 1.0)
    longest_mid_pt = longest_crv.PointAt(.5)

    if second_one:

        second_longest_crv.Domain = rg.Interval(0, 1.0)
        second_longest_mid_pt = longest_crv.PointAt(.5)

        split_lines = [
            rg.Line(pin_point, second_longest_mid_pt),
            rg.Line(pin_point, longest_mid_pt)    
        ]

        return split_lines

    else:

        split_line = rg.Line(pin_point, longest_mid_pt)

        return split_line


def createLinks(pin_pts, connection_count = 2, max_main_line = 100.0, start_end_alfa = .5, mid_alfa = .25):

    pin_pts = [rg.Point3d(pt.X, pt.Y, 0.0) for pt in pin_pts]

    main_links, link_lines, pin_pt_sets = [], [], []
    split_lines = []

    pin_count = len(pin_pts)

    for pt_i, pt in enumerate(pin_pts):

        if pt_i == 0:

            main_link, link_line_set, pt_set = start(pt, pin_pts[pt_i + 1], connection_count, start_end_alfa)

            main_links.append(main_link)
            link_lines.extend(link_line_set)
            pin_pt_sets.append(pt_set)

        elif pt_i == pin_count - 1:

            _, link_line_set, pt_set = end(pin_pts[pt_i - 1], pt, connection_count, start_end_alfa)

            # main_links.append(main_link)
            link_lines.extend(link_line_set)
            pin_pt_sets.append(pt_set)

        else:

            main_link, link_line_set, pt_set = mid(pin_pts[pt_i - 1], pt, pin_pts[pt_i + 1], connection_count, mid_alfa)

            main_links.append(main_link)
            link_lines.extend(link_line_set)
            pin_pt_sets.append(pt_set)

    # generating extra line division in case the main lines are too long

    b_mid_pts = []
    mid_links = []

    for i in range(pin_count - 1):

        pt_0 = pin_pts[i]
        pt_1 = pin_pts[i + 1]

        distance = pt_0.DistanceTo(pt_1)

        if distance > max_main_line:

            _, loc_link_set, _ = start(pt_0, pt_1, 2, alfa = 1.570796)

            split_count = int(round(distance / max_main_line))

            b_pts = lineInterpolate(pt_0, pt_1, split_count)

            loc_mid_pts = []

            if len(b_pts) > 1:

                # generating mid points between the base points if necessary

                for i in range(len(b_pts) - 1):

                    loc_mid_pts.append(rg.Point3d( (b_pts[i] + b_pts[i+1]) * .5) )

            for b_pt in b_pts:

                trans_m = rg.Transform.Translation(rg.Vector3d(b_pt - pt_0))

                mid_links.extend(copyTransformSet(loc_link_set, trans_m))

        b_mid_pts.append(loc_mid_pts)

    # generating the split lines

    for i, pin_pt_set in enumerate(pin_pt_sets):

        split_lines.append(longestSegment(pin_pts[i], pin_pt_set))

    return main_links, link_lines, split_lines, pin_pt_sets, mid_links, b_mid_pts


def pinMaker(pin_pts, pin_height, bot_rad, top_rad, resolution = 16):

    return [Pin(pt, pin_height, bot_rad, top_rad, resolution) for pt in pin_pts]

def extendTrim(inner_crv, outer_crv, line_set):

    line_set.trimLines(outer_crv, True)
    line_set.trimLines(inner_crv, False)

def linkClosestPoints(link, pts):

    extra_pt_set = []

    lines = link.createLines()

    for line in lines:

        for pt in pts:

            extra_pt_set.append( line.ClosestPoint(pt, False) )

    return extra_pt_set

def joinShape(prev_crv, next_crv, line_set, extend_trim = True, crossing = False):

    if extend_trim:

        extendTrim(prev_crv, next_crv, line_set)
    
    result_crvs_0, _ = layer2ptIntersect(prev_crv, line_set.Start)
    main_crv = curveToPolyline(longestCurve(result_crvs_0))

    result_crvs_1, _ = layer2ptIntersect(next_crv, line_set.End)
    next_crv = curveToPolyline(longestCurve(result_crvs_1))

    main_crv, next_crv = list(main_crv), list(next_crv)

    
    if not(crossing):

        pt_set = main_crv + next_crv

    else:

        crossing_distance = 4.0

        start0, start1 = main_crv[0], main_crv[-1]
        end0, end1 = next_crv[-1], next_crv[0]

        distance0 = start0.DistanceTo(end0)
        distance1 = start1.DistanceTo(end1)

        exPt0_0 = crossing_distance
        exPt0_1 = distance0 - crossing_distance

        exPt1_0 = crossing_distance
        exPt1_1 = distance1 - crossing_distance

        # swapping & reversing set 1

        pt0_0 = interpolatePts(start0, end0, exPt0_0)
        pt0_1 = interpolatePts(start0, end0, exPt0_1)

        pt1_1 = interpolatePts(start1, end1, exPt1_0)
        pt1_0 = interpolatePts(start1, end1, exPt1_1)

        pt_set = main_crv + [pt0_0, pt0_1] + next_crv + [pt1_0, pt1_1]

    return pt_set + [pt_set[0]]
        

def linkSetGeneration(lines, spacing, amount = 2):

    link_set = []

    for line in lines:

        loc_line_set = LineSet(line, spacing, amount)
        loc_line_set.createLines()

        link_set.append(loc_line_set)

    return link_set


def makeMainShape(pins, main_link_set, height, bottom_shift = None):

    main_crv = pins[0].createSlice(height).ToPolylineCurve()

    if not(bottom_shift == None):

        print("I am offsetting the bottom layer with %s" % bottom_shift)
        
        main_crv = offsetCurveSet(main_crv, bottom_shift, "outside", count = 2)[1].ToNurbsCurve()

    inner_crvs = [dc(main_crv)]

    mv_m = rg.Transform.Translation(rg.Vector3d(0,0,height))

    main_links = []

    for i, main_link in enumerate(main_link_set):

        con_line_set = dc(main_link)
        con_line_set.Transform(mv_m)

        next_crv = pins[i + 1].createSlice(height).ToPolylineCurve()

        if not(bottom_shift == None):

            print("I am offsetting the bottom layer with %s" % bottom_shift)
            
            next_crv = offsetCurveSet(next_crv, bottom_shift, "outside", count = 2)[1].ToNurbsCurve()

        inner_crvs.append(dc(next_crv))

        current_pt_set = joinShape(main_crv, next_crv, con_line_set)

        main_crv = rg.Polyline(current_pt_set).ToPolylineCurve()

        main_links.append(con_line_set)

    return main_crv, current_pt_set, main_links, inner_crvs


def addLink(polycrv, side_link, open_end = True, start_pts = False, safety_dis = True, start_dis = (20.0, 15.0)):

    result_crvs, _ = layer2ptIntersect(polycrv, side_link.Start)
    pt_set = list(curveToPolyline(longestCurve(result_crvs)).ToArray())

    if pt_set[0].DistanceTo(side_link.Start[1]) < .001:

        # start_pts = list(side_link.Start).reverse()
        end_pts = list(side_link.End)
        end_pts.reverse()

    else:

        # start_pts = list(side_link.Start)
        end_pts = list(side_link.End)


    if open_end:

        pt_set = [end_pts[1]] + pt_set + [end_pts[0]]

    elif start_pts:

        if safety_dis:

            start_dis = [start_dis[0], start_dis[1], start_dis[1], start_dis[0]]

            vecs = [
                rg.Vector3d(pt_set[-2] - pt_set[-1]),
                rg.Vector3d(end_pts[0] - pt_set[-1]),
                rg.Vector3d(end_pts[1] - pt_set[0]),
                rg.Vector3d(pt_set[1] - pt_set[0])
            ]

            [vec.Unitize() for vec in vecs]

            vecs = [vec * start_dis[vec_i] for vec_i, vec in enumerate(vecs)]

            b_pts = [pt_set[-1], pt_set[-1], pt_set[0], pt_set[0]]

            ex_pts = [rg.Point3d(b_pt + vecs[i]) for i, b_pt in enumerate(b_pts)]
            ex_pts = ex_pts[:2] + end_pts + ex_pts[2:]

            print(len(ex_pts))

            pt_set = pt_set[1:-1] + ex_pts # + [pt_set[1]]

        else:

            pt_set = pt_set[1:-1] + end_pts + [pt_set[1]]
    
    else:

        # pt_set = pt_set + side_link.joinLines(False) + [pt_set[0]]
        
        pt_set = pt_set + end_pts + [pt_set[0]]

    return pt_set


def makeSideLinks(main_crv, exterior_crv, link_set, height):

    mv_m = rg.Transform.Translation(rg.Vector3d(0,0,height))

    side_link_set = []
    main_crv_pt_set = []

    for side_link in link_set:

        loc_side_link = dc(side_link)
        loc_side_link.Transform(mv_m)

        extendTrim(main_crv, exterior_crv, loc_side_link)

        side_link_set.append(loc_side_link)

        main_crv_pt_set = addLink(main_crv, loc_side_link, False)
        main_crv = rg.Polyline(main_crv_pt_set).ToPolylineCurve()

    return main_crv_pt_set, side_link_set


def makeInnerCurve(inner_crvs, main_links, side_links, end_link = None, loc_extra_pts = None, mid_links = None, diamond_settings = (False, False, (15.0, 10.0))):

    inner_crv_count = len(inner_crvs)

    main_crv = dc(inner_crvs[0])

    # reading in the diamond settings
    start_mid_pts, safety_dis, start_dis = diamond_settings

    if inner_crv_count > 1:

        print("I have to do more!")

        for i in range(inner_crv_count - 1):

            current_pt_set = joinShape(main_crv, inner_crvs[i + 1], main_links[i], False, True)

            main_crv = rg.Polyline(current_pt_set).ToPolylineCurve()

    if not(loc_extra_pts == None):

        for pt in loc_extra_pts:

            _, t_val = main_crv.ClosestPoint(pt)

            main_crv.ChangeClosedCurveSeam(t_val)

    for side_link in side_links:

        print("I am adding a side_link!")

        pt_set = addLink(main_crv, side_link, open_end = False)

        main_crv = rg.Polyline(pt_set + [pt_set[0]]).ToPolylineCurve()

    for mid_link in mid_links:
        
        print("I am here?")

        pt_set = addLink(main_crv, mid_link, open_end = False, start_pts = start_mid_pts, safety_dis = safety_dis, start_dis = start_dis)

        main_crv = rg.Polyline(pt_set + [pt_set[0]]).ToPolylineCurve()

    if not(end_link == None):

        print("I am adding the end_link!")

        pt_set = addLink(main_crv, end_link, True)

        main_crv = rg.Polyline(pt_set).ToPolylineCurve()

    return main_crv




# def createLinkChain(pins, height, main_links, link_lines, split_lines, outer_part, ):