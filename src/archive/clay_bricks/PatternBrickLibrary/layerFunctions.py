# layer slicing functions

import ghpythonlib
import Rhino.Geometry as rg
from generalFunctions import *
import math
from copy import deepcopy as dc

class LineSet(object):

    def __init__(self, line, distance, count):

        self.l = line
        self.d = distance
        self.c = count

    def createLines(self):

        start_pt, end_pt = self.l.PointAt(0.0), self.l.PointAt(1.0)
        c_pt = ( start_pt + end_pt ) * .5

        y_vec = rg.Vector3d(end_pt - start_pt)
        y_vec.Unitize()
        y_vec = rotObject90Degree(y_vec)

        mv_vec_0 = - y_vec * self.d * (self.c - 1) * .5
        mv_vec = rg.Vector3d(y_vec * self.d)
        
        mv_0 = rg.Transform.Translation(mv_vec_0)
        mv = rg.Transform.Translation(mv_vec)

        self.lines = []

        tmp_line = dc(self.l)
        tmp_line.Transform(mv_0)

        self.lines = [dc(tmp_line)]

        for i in range(self.c - 1):

            tmp_line.Transform(mv)

            self.lines.append(dc(tmp_line))

        return self.lines

    def trimLines(self, crv, extend = False):

        crv = polylineTypesToCurve(crv)

        for line in self.lines:

            # line.Domain = rg.Interval(0, 1)

            pts = lineCurveIntersection(line, crv)

            if extend:

                # line.From = line.From

                line.To = pts[0]

            else:
                
                line.From = pts[-1]

                # line.To = line.To

        return self.lines

    def joinLines(self, open_link = False):

        # if I am open, that means that two sets will be returned and that the 
        # lines that don't connect will be shortened
        
        # pt_set generation

        if (open_link and (len(self.lines) > 3)):

            line_count = len(self.lines)

            lines = dc(self.lines)

            for line_i in range(2, line_count, 1):

                lines[line_i].Extend(- self.d)

        else:

            lines = self.lines

        pt_set = []

        for line_i, line in enumerate(lines):

            if line_i % 2 == 1:

                pt_set.append(line.To)
                pt_set.append(line.From)

            else:

                pt_set.append(line.From)
                pt_set.append(line.To)

        pt_set = pt_set[1:-1]

        if open_link:

            return pt_set[:-1], pt_set[-1:]

        else:

            return pt_set[1:-1]

    @ property
    def Start(self):

        return self.getStartEnd(True)

    @ property
    def End(self):

        return self.getStartEnd(False)

    def getStartEnd(self, start = True):

        if start:

            return self.lines[0].PointAt(0.0), self.lines[-1].PointAt(0.0)

        else:

            return self.lines[-1].PointAt(1.0), self.lines[0].PointAt(1.0)

    def Transform(self, trans_matrix):

        for l in self.lines:

            l.Transform(trans_matrix)


class PolyCurveSplit(object):

    def __init__(self, crv, intersection_pts):

        self.base_crv = crv

        self.intersectOrganization(intersection_pts)

        self.first_split = False
        self.second_split = False

    def intersectOrganization(self, pts):

        self.pt_0_a = pts[0][0]
        self.pt_1_a = pts[0][1]

        self.pt_0_b = pts[1][0]
        self.pt_1_b = pts[1][1]

    def firstSplit(self, back = True):

        self.first_split = True

        self.back = back

        if self.back:
            
            pts = [self.pt_0_a, self.pt_0_b]
            self.second_set = [self.pt_1_a, self.pt_1_b]

            crvs, _ = layer2ptIntersect(self.base_crv, pts)

        else:

            pts = [self.pt_1_a, self.pt_1_b]
            self.second_set = [self.pt_0_a, self.pt_0_b]

            crvs, _ = layer2ptIntersect(self.base_crv, pts)

        lengths = [rg.Curve.GetLength(crv) for crv in crvs]

        lengths, crvs = zip(*sorted(zip(lengths, crvs)))

        self.main_crv = crvs[-1]

        return self.main_crv

    def secondSplit(self, reverse = True):

        self.reverse = reverse

        self.second_split = True

        split_ts = [closestPointOnCurve(self.main_crv, pt)[2] for pt in self.second_set]

        result_crvs = [crv for crv in self.main_crv.Split(split_ts)]
        result_crvs.pop(1)

        if not(self.back) and reverse:

            result_crvs = result_crvs[::-1]

        self.crv_a = result_crvs[0]
        self.crv_b = result_crvs[1]

        if not(self.back) and not(reverse):

            self.crv_a.Reverse()
            self.crv_b.Reverse()            

        return result_crvs

    def generatePts(self):

        if self.first_split:

            main_crv = curveToPolyline(self.main_crv)
            
            self.main_pts = [pt for pt in main_crv.ToArray()]

        if self.second_split:

            crv_a = curveToPolyline(self.crv_a)
            crv_b = curveToPolyline(self.crv_b)

            self.pts_a = [pt for pt in crv_a.ToArray()]
            self.pts_b = [pt for pt in crv_b.ToArray()]

            if self.back:

                self.pts_a.reverse()
                self.pts_b.reverse()


class LinkingLayers(object):

    def __init__(self, crvs, split_distance, side_bool = True, split_type = "detached", split_line = None):

        self.base_crvs = self.crvCheck(crvs)

        self.split_d = split_distance
        self.side_bool = side_bool

        # to-do find logic to communicate this
        self.split_type = split_type

        self.splitLineGeneration(split_line)

        if split_type == "detached":

            self.reverse_second_split = True
        
        elif split_type == "crossing":

            self.reverse_second_split = False


    def crvCheck(self, crvs):

        new_crvs = []
        
        for crv in crvs:

            new_crv = polylineTypesToCurve(crv)

            new_crvs.append(new_crv)

        return new_crvs


    def splitLineGeneration(self, split_line = None, angle = None):

        if split_line == None:

            print("no line given")

            self.base_crvs[0].Domain = rg.Interval(0,10)

            pts = [self.base_crvs[0].PointAt(i) for i in range(10)]

            pt_sum = rg.Point3d(0,0,0)

            for pt in pts:

                pt_sum += pt

            pt_sum /= 10

            first_pt = pt_sum

            self.split_line = rg.Line(first_pt, rg.Point3d(0,0,first_pt.Z))

        else:

            print("I have given a line")

            self.split_line = split_line

        self.split_axis = rotObject90Degree(self.split_line, other_angle = angle)

        self.split_a, self.split_b = LineSet(self.split_line, self.split_d, 2).createLines()


    def createOrganisedCurves(self):

        self.organised_crvs = []

        pts_output = []

        for crv in self.base_crvs:

            pt_sets = []

            print(type(self.split_a))
            print(self.split_a.To.Z)

            pts, _ = crvIntersector(crv, self.split_a)

            print(pts)

            pts_a = extremePtsOfAxis(pts, self.split_axis)

            pt_sets.append(pts_a)

            pts_output.extend(pts)

            pts, _ = crvIntersector(crv, self.split_b)

            pts_b = extremePtsOfAxis(pts, self.split_axis)

            pt_sets.append(pts_b)

            pts_output.extend(pts)

            self.organised_crvs.append(PolyCurveSplit(crv, pt_sets))

        # org_crvs = [crv.base_crv for crv in self.organised_crvs]

        main_crvs = []
        second_sets = []
        crv_set_a = []
        crv_set_b = []

        for crv_i, crv in enumerate(self.organised_crvs):

            current_side_bool = bool((crv_i + self.side_bool) % 2)

            print(current_side_bool)

            main_crv = crv.firstSplit(current_side_bool)

            main_crvs.append(main_crv)

        for i in range(1, len(self.organised_crvs), 1):

            second_set = self.organised_crvs[i].secondSplit(self.reverse_second_split)

            crv_set_a.append(second_set[0])
            crv_set_b.append(second_set[1])

            second_sets.extend(second_set)

        start_crv = main_crvs[0]
        
        return pts_output, start_crv, second_sets, crv_set_a, crv_set_b


    def joinCrvs(self):

        [crv.generatePts() for crv in self.organised_crvs]

        a_pt_set = []
        b_pt_set = []

        for crv in self.organised_crvs:

            if crv.second_split:

                b_pt_set.append(crv.pts_a)
                a_pt_set.append(crv.pts_b)

            else:

                m_pt_set = crv.main_pts

        a_pt_set.reverse()
        m_pt_set.reverse()

        total_pt_set = []

        for pt_set in a_pt_set:

            total_pt_set.extend(pt_set)

        total_pt_set += m_pt_set

        for pt_set in b_pt_set:

            total_pt_set.extend(pt_set)

        return total_pt_set