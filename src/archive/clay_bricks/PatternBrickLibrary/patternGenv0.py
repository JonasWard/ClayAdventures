import Rhino.Geometry as rg
import math

# grasshoppper variables

# geometric variables
base_points
normals
layer_count
layer_height

# pattern variables
min_max_val
period
phase_shift

class PointWithNormal(object):

    def __init__(self, pt, normal):

        self.o = pt
        self.n = normal

    def new_pt(self, scale_val = 0):

        return rg.Point3d(self.o + self.n * scale_val)

base_layer_set = []

for i, pt in enumerate(base_points):

    local_pt = rg.Point3d(pt.X, pt.Y, 0.0)

    base_layer_set.append(PointWithNormal(local_pt, normals[i]))

print(base_layer_set)

curve_list = []

class PatternMap(object):

    def __init__(self, base_crv, origin = rg.Point3d(0,0,0)):

        self.base_crv

    def subdivide(self, div_length):

        length = self.base_crv.GetLength()
        divisions = int(length / div_length)
        self.div_length = length / divisions
        
        t_vals = self.base_crv.DivideByLength(self.div_length, True)

        planes = [self.base_crv.FraneAt(t) for t in t_vals]

        # self.base_lay = 

        return planes

    def generate(self, layer_height, layer_count):

        self.lay_h = layer_height
        self.lay_c = layer_height

        # for z_in in layer_count:

        #     z_val = z_in * self.lay_h

        #     for x_in, pt in enumerate(self.base_lay):

        #         scale_val = math.sin(local_phase_shift + x_in / period) * min_max_val

        #         shifted_pt = o_pt.new_pt(scale_val)

        #         local_crv_set.append(shifted_pt + z_mv_pt)

        #     local_crv_set.append(local_crv_set[0])

        #     curve_list.append(rg.Polyline(local_crv_set))
