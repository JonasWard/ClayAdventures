# polylineInterfaceClass

import Rhino.Geometry as rg
from ghpythonlib.components import Area as gh_area
import math

class ClayPolyline(object):

    def __init__(self, pt_set, closed = False):

        self.pts = pt_set
        self.closed = closed

        self.cnt = len(self.pts)

        self.has_crv_rep = False

        self.tolerance = .01


    def __add__(self, other):

        if isinstance(other, list):

            other = ClayPolyline(other)

        return ClayPolyline(self.pts + other.pts)


    def __updatePolyline__(self, new_set = None):

        if not(new_set == None):
        
            self.pts = new_set

        if self.has_crv_rep:

            self.GetCurve()

        self.cnt = len(self.pts)

    @ staticmethod
    def StartIndex(self):

        return 0

    @ staticmethod
    def Start(self):

        return self.pts[self.StartIndex]

    @ staticmethod
    def EndIndex(self):

        return len(self.pts) - 1

    @ staticmethod
    def End(self):

        return self.pts[self.EndIndex]


    def GetLength(self):

        if not(self.has_crv_rep):

            self.GetCurve()

        return self.crv_rep.GetLength()

    def GetArea(self):

        # this is a hack using the rhino grasshopper component
        area, _ = gh_area(x)

        return area

    def Reverse(self):

        self.__updatePolyline__(self.pts[::-1])


    def GetCurve(self):

        self.has_crv_rep = True

        self.crv_rep = rg.Polyline(self.pts + self.Start if self.closed else self.pts).ToNurbsCurve()

        return self.crv_rep


    def ClosestPoint(self):

        if not(self.has_crv_rep):

            self.GetCurve()


    def PointAtLength(self, val, return_index = False):

        if val < 0.0:

            print("you gave me a negative value, here is the first point")

            new_pt = self.Start
            i = self.StartIndex

        elif val > self.GetLength():

            print("""you gave me a value larger than the length of the curve /n"
            therefore I return you the last point!""")

            new_pt = self.End
            i = self.EndIndex

        else:

            length = 0.0

            for i in range(self.StartIndex, self.EndIndex, 1):

                pt_0 = self.pts[i]
                pt_1 = self.pts[i + 1]

                local_length = pt_0.DistanceTo(pt_1)

                if length + local_length > val:

                    break

                else:

                    length += local_length

            new_pt = interpolatePts(pt_0, pt_1, val - length)

        if return_index:

            return new_pt, i

        else:

            return new_pt
    
    def ReaseamAt(self, value, index_or_length = "index"):

        if self.closed:

            if index_or_length == "index":

                pl_a, pl_b = self.SplitAtIndex(value)

    def SplitAtIndex(self, *indexes):

        indexes = list(indexes).sort()
        indexes.reverse()

        pl_list = []

        local_pt_list = self.pts[:]

        for index in indexes:

            end = math.floor(index)
            start = math.ceil(index)

            delta = index - end

            if delta < self.tolerance:

                # case that the polyline is very short

                pass


    def SplitAtLength(self, *lengths):

        pass

    def Orient(self):

        if self.closed:
            
            

        else:

            print("I can not be oriented")


    def Shorten(self, length, side = "start"):

        polyline_length = self.GetLength()

        # length check:

        length = abs(length)

        half_pl_length = polyline_length * .5

        if length > half_pl_length:

            # reducing the length value to a mod of the polyline

            length = length % half_pl_length

        if side == "start" or side == "both":

            new_pt, pt_index = self.PointAtLength(length, True)

            self.__updatePolyline__([new_pt] + self.pts[pt_index + 1:])

        if side == "end" or side == "both":

            new_pt, pt_index = self.PointAtLength(polyline_length - length, True)

            self.__updatePolyline__(self.pts[:pt_index] + [new_pt])

    def RemoveIndex(self, *index_args):

        indexes = list(index_args).sort()
        indexes.reverse()

        for index in indexes:

            if index > len(self.pts):

                print("You can only remove points at a certain index if that index is within the domain ...")

            else:

                self.pts.pop(index)

        self.__updatePolyline__()

    def AddPoint(self, *pt_args):

        self.pts += list(pt_args)

        self.__updatePolyline__()

    def Offset(self, *offset_args):

        offset_set = []

        for offset_val in offset_args:

            offset_crv = self.crv_rep.Offset(pln, offset_val, .01, o_type)[0]
            offset_crv = offset_crv.ToPolyline()

        offset_set.append(offset_crv)

        if len(offset_set) == 1:

            return offset_set[0]

        else:

            return offset_set

    def Close(self, collapse_distance = 1.0):

        if not self.closed:

            print("I have to be closed")

        if self.Start.DistanceTo(self.End) < collapse_distance:

            print("& I have to collapse onto myself")

            self.RemoveIndex(self.cnt - 1)
        



    

