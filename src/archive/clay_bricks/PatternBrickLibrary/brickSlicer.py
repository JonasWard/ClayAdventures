import Rhino.Geometry as rg
# import ghpythonlib.components as gh
import math
from generalFunctions import *
from simpleStartStop import *
from copy import deepcopy as dc
# import Rhino.DocObjects as rd

class Brick(object):

    def __init__(self, shell = None, pins = None, patterns = None, l_type = None, p_type = None):

        if shell == None:

            self.has_shell = False

        else:

            self.has_shell = True
            
            self.shell_obj = shell

        if pins == None:

            self.has_pins = False

        else:

            self.has_pins = False

            self.pin_objs = pins

        if patterns == None:

            self.has_patterns = False

        else:

            self.has_patterns = True

            self.patterns = patterns

        if l_type == None:

            self.l_type = LinkType()

        else:

            self.l_type = l_type

        if p_type == None:

            self.p_type = PrintSettings()

        else:

            self.p_type = p_type

        if not(self.has_pins or self.has_shell):

            print("can't have no pins or no shell")
            print("I'll operated under the assumption,")
            print("you wanted to do a simple circular column")

            self.has_shell = True

            tmp_circle = rg.Circle(
                rg.Point3d(0.0,0.0,0.0),
                35.0
            ).ToNurbsCurve()

            self.shell_obj = Shell(geo = tmp_circle)

    def createLayers(self, layer_height, body_height, total_height, start_height = 0.0):

        height = start_height

        self.brickLayers = []

        while height < total_height:

            if height < body_height:

                self.brickLayers.append(self.createLayer(height, True))

            height += layer_height

    def createLayer(self, height, shell = True):

        if self.has_shell and shell:

            shell_crv = self.__shellPart(height)
        
        if self.has_pins and shell:

            pin_crvs = self.__pinSet(height, False)

        elif self.has_pins and not(shell):

            pin_crvs = self.__pinSet(height, True)

    def __shellPart(self, height):

        return self.shell_obj.createSlice(height)

    def __pinSet(self, height, inside = False):

        return [pin.createSlice(height) for pin in self.pin_objs]


class OrganisedCurve(object):

    def __init__(self, base_crv, linked_obj, direction = True):

        self.base_crv = curveRotator(base_crv)

    def split(self, object):

        pass

    def applyPattern(self, pattern, logic = None, periodic = False):

        pass

    def join(self):

        pass

    def alignSeams(self, ref_pt = None):

        if ref_pt == None:

            pass
            # means it's the first layer

        else:

            pass

    def organiseSplits(self, ref_pts = None):

        pass


class BrickLayer(object):

    def __init__(self, brick, height):

        pass


class Shell(object):

    def __init__(self, geo, offset_count = 1, l_type = None):

        self.geo_type = rhinoGeometryObjectType(geo)
        self.geo = geo

    def moveToPoint(self, pt = None):

        if pt == None:

            placingInPlace(self.geo)

        else:

            placingInPlace(self.geo, pt)

    def createSlice(self, height):

        if self.geo_type == "crv":

            return self.__ifCrv(height)

        elif (self.geo_type == 'brep') or (self.geo_type == 'mesh'):

            return self.__ifMeshBrep(height)

    def __ifCrv(self, height, other = None):

        if other == None:

            slice_crv = dc(self.geo)

        else:

            slice_crv = other

        placingInPlace(slice_crv, z_val=height)

        return slice_crv

    def __ifMeshBrep(self, height):

        try:

            h_pl = rg.Plane(rg.Point3d(0,0,height), rg.Vector3d(0,0,1))

            if self.geo_type == 'brep':

                contour_crv = rg.Brep.CreateContourCurves(geometry, h_pl)[0]

            elif self.geo_type == 'mesh':

                contour_crv = rg.Mesh.CreateContourCurves(geometry, h_pl)[0]

            self.previous_crv = contour_crv

        except:

            contour_crv = self.__ifCrv(height, self.previous_crv)

            self.previous_crv = contour_crv

        return contour_crv


class Pin(object):

    def __init__(self, b_pt, height, bot_rad, top_rad, resolution = 0, l_type = None, p_type = None):

        self.b_pt = b_pt
        self.h = height
        self.bot_r = bot_rad
        self.top_r = top_rad

        self.delta_r = top_rad - bot_rad

        self.res = int(resolution)

        if self.res > 0:

            self.res_delta = 6.2831852 / self.res

        self.l_type = l_type
        self.p_type = p_type

    def createGeometry(self):

        bot_c = rg.Circle(self.b_pt, self.bot_r).ToNurbsCurve()
        top_c = rg.Circle(self.b_pt + rg.Point3d(0,0,self.h), self.top_r).ToNurbsCurve()

        return rg.Brep.CreateFromLoft(
            [bot_c, top_c],
            rg.Point3d.Unset,
            rg.Point3d.Unset,
            rg.LoftType.Loose,
            False
        )[0]

    def bPt(self, height):

        return rg.Point3d(self.b_pt.X, self.b_pt.Y, height)

    def radius(self, height):

        rel_height = (height - self.b_pt.Z) / self.h
        r = self.bot_r + rel_height * self.delta_r

        return r

    def helixPoint(self, alfa, height):

        r = self.radius(height)

        return rg.Point3d(
            r * math.cos(alfa) + self.b_pt.X,
            r * math.sin(alfa) + self.b_pt.Y,
            height
        )
        
    def createSlice(self, height):

        circle = rg.Circle(
            self.bPt(height),
            self.radius(height)
        )

        if self.res == 0:
        
            return circle

        else:

            pt_set = [circle.PointAt(self.res_delta * i) for i in range(self.res)]

            return rg.Polyline(pt_set + [pt_set[0]])

    def helix(self, start_h = 150.0, end_h = 260.0, start_pt = None, layer_h = 2.5, start_alfa = 0.0):

        alpha_delta = math.pi * 2.0 / self.res
        h_delta = layer_h / self.res

        if not(start_pt == None):

            start_h = start_pt.Z + layer_h * .5

            start_alfa = vectorAngle(start_pt)

        height = start_h
        alfa = start_alfa

        pt_list = []

        while height < end_h:

            pt_list.append(self.helixPoint(alfa, height))

            height += h_delta
            alfa += alpha_delta

        return pt_list


def slicing(geometry, heights):

    object_height = heights[-1]

    geo_type = rhinoGeometryObjectType(geometry)

    geo_height = placingInPlace(geometry)

    contour_set = []

    if (geo_type == 'brep') or (geo_type == 'mesh'):
        # types that need to be contoured
        
        for crv_i, loc_h in enumerate(heights):

            if loc_h > geo_height:

                mv_up = rg.Transform.Translation(rg.Vector3d(0,0,loc_h - heights[crv_i - 1]))

                crv = dc(crv)
                crv.Transform(mv_up)

                contour_set.append(crv)

            else:

                mv_up = rg.Transform.Translation(rg.Vector3d(0,0,loc_h))

                h_pl = rg.Plane(rg.Point3d(0,0,loc_h), rg.Vector3d(0,0,1))

                if geo_type == 'brep':

                    crv = rg.Brep.CreateContourCurves(geometry, h_pl)[0]

                elif geo_type == 'mesh':

                    crv = rg.Mesh.CreateContourCurves(geometry, h_pl)[0]
                
                contour_set.append(crv)


    elif geo_type == 'crv':

        for loc_h in heights:

            mv_up = rg.Transform.Translation(rg.Vector3d(0,0,loc_h))
            
            crv = dc(geometry)
            crv.Transform(mv_up)

            contour_set.append(crv)

    else:

        print("%s is not supported" % geo_type)

    return contour_set


def layerIntersect(contour_crv, center_axis, slicing_object = None):

    # in case no slicing object is given

    if slicing_object == None:

        slicing_object = center_axis

    # two halves

    # c_pt = center_axis.PointAt(.5)
    # rot = rg.Transform.Rotation(math.pi * .5, c_pt)

    split_axis = dc(center_axis)
    # split_axis.Transform(rot)

    split_axis = moveToSameHeight(contour_crv, split_axis)

    # doing the intersections

    _, t_vals = crvIntersector(contour_crv, split_axis)

    contour_crv.ChangeClosedCurveSeam(t_vals[0])

    pts, _ = crvIntersector(contour_crv, slicing_object)

    # sorting based on distance from the split axis

    pts = extremePtsOfAxis(pts, split_axis)

    return layer2ptIntersect(contour_crv, pts)


def curveSetSorter(crv_set):

    # sorts a set of two curves based on which one is stacked on top of the other

    pt_0 = crv_set[0][0].PointAt(.5)
    pt_1 = crv_set[0][1].PointAt(.5)

    pt_set_a = [pt_0]
    pt_set_b = [pt_1]

    for crv_i in range(1, len(crv_set), 1):

        pt_0_crv_0, dis_0, _ = closestPointOnCurve(crv_set[crv_i][0], pt_0)
        pt_0_crv_1, dis_1, _ = closestPointOnCurve(crv_set[crv_i][1], pt_0)

        if dis_0 < dis_1:

            pt_0 = pt_0_crv_0

        else:

            pt_0 = pt_0_crv_1

            # switching the curve location over

            tmp_crv_1 = dc(crv_set[crv_i][0])
            crv_set[crv_i][0] = crv_set[crv_i][1]
            crv_set[crv_i][1] = tmp_crv_1

        # also know pt_1_crv_1

        pt_1, _, _ = closestPointOnCurve(crv_set[crv_i][1], pt_1)

        pt_set_a.append(pt_0)
        pt_set_b.append(pt_1)

    return crv_set, pt_set_a, pt_set_b

def splitter(contour_set, slicing_object = None, split_type = "longest"):

    # types of splitting:
    # along it's >longest< direction - only one that requires no object
    # using an >object<
    # using an object but only >first layer< - only one that can work with curves

    geo_type = rhinoGeometryObjectType(slicing_object)

    # checking invalidities
    if geo_type == 'other' and not(split_type == "longest"):

        split_type = "longest"
        print("you have given a none usuable geometry to split with, so I/n")
        print("reverted to the longitudinal splitting!/n")

    elif geo_type == 'crv' and split_type == "object":

        split_type = "first layer"
        print("you have given a crv which you can only use to split the first/n")
        print("layer with, so I reverted to first layer splitting!/n")

    split_contour_set = []

    center_axis = crvOrienter(contour_set[0])

    if split_type == "object":

        for crv in contour_set:

            crv_set, _ = layerIntersect(crv, center_axis, slicing_object)

            split_contour_set.append(crv_set)
    
    else:

        # first layer
        
        if split_type == "first_layer":

            crv_set, pts = layerIntersect(contour_set[0], center_axis, slicing_object)

        else:

            # means it's a longest type split

            crv_set, pts = layerIntersect(contour_set[0], center_axis, slicing_object = None)

        split_contour_set.append(crv_set)

        for i in range(1, len(contour_set), 1):

            crv_set, pts = layer2ptIntersect(contour_set[i], pts)

            split_contour_set.append(crv_set)

    # setting domain from 0 to 1

    for crv_set in split_contour_set:

        for crv in crv_set:

            crv.Domain = rg.Interval(0.0, 1.0)

    crv_sets, pts_a, pts_b = curveSetSorter(split_contour_set)

    split_contour_vis_set_a = [crv_set[0] for crv_set in crv_sets]
    split_contour_vis_set_b = [crv_set[1] for crv_set in crv_sets]

    return crv_sets, split_contour_vis_set_a, split_contour_vis_set_b, [pts_a, pts_b]