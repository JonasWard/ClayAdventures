import Rhino.Geometry as rg
import math

class Vertex(object):

    def __init__(self, pt = rg.Point3d(0,0,0), normal = rg.Point3d(0,0,0), rel_loc = rg.Point3d(0,0,0), is_neg = False):

        self.o = pt
        self.v = pt
        
        self.n = normal
        self.n_scale = 1.0

        self.rel_loc = rel_loc

        self.vec_version = rg.Point3d(x_val, y_val, 0.0)

        self.is_neg = is_neg


    def numeric_distance(self, other, radius = 0.0):

        # return ((self.x_val - other.x_val) ** 2 + (self.y_val - other.y_val) ** 2) ** .5

        return self.vec_version.DistanceTo(other.vec_version)


    def x_distance(self, other):

        return abs(self.x_val - other.x_val)


    def move_pt(self, mv_pt):

        return Vertex(self.o + mv_pt, self.n, self.x_val, self.y_val)
        

    def warp_pt(self, scale_val = 0):

        self.v = rg.Point3d(self.o + self.n * (scale_val * self.n_scale))

    def distance_function(self, x_spacing = 20.0, y_spacing = 20.0, layer_shift = 2.0, rot_alfa = 0.0, x_scale_val = 1.0):
        
        x, y = self.x_val, self.y_val

        if not(rot_alfa == 0.0):
            
            x_new = math.cos(rot_alfa) * x - math.sin(rot_alfa) * y
            y_new = math.sin(rot_alfa) * x + math.cos(rot_alfa) * y
            
            x, y = x_new, y_new
        
        layer_shift = float(layer_shift)
        
        abs_loc_y = y % y_spacing
        layer_count = float(math.floor((y - abs_loc_y) / y_spacing))
        
        # print("layer_count %s" % layer_count)
        # print("layer_shift %s" % layer_shift)
        
        x_shift = (layer_count / layer_shift) * x_spacing
        
        # print("x_shift %s" % x_shift)
        
        loc_x = ((x + x_shift) % x_spacing) / x_spacing
        loc_y = abs_loc_y / y_spacing
        
        distance = math.sqrt((loc_x - .5) ** 2 + (loc_y - .5) ** 2)
        
        return distance


def moveSet(layer_set, reference_set, pattern_set = [1], div_l = 3.0, direction_val = -1, item = 0):

    crv_l = layer_set[0][item].GetLength()
    div_c = int(crv_l / div_l)
    div_l = crv_l / float(div_c)
    lay_h = float(reference_set[1].PointAt(0.0).Z - reference_set[0].PointAt(0.0).Z)

    pattern_part = []
    other_part = []

    offset_crvs = []

    for ref_i, layer in enumerate(layer_set):
        
        a_crv = layer[item]
        b_crv = layer[(item + 1) % 2]
        c_crv = reference_set[ref_i]

        local_l_a = a_crv.GetLength()
        local_l_b = b_crv.GetLength()
        
        local_div_l_a = local_l_a / div_c
        local_div_l_b = local_l_b / div_c
        
        t_vals_a = a_crv.DivideByLength(local_div_l_a, True)
        t_vals_b = b_crv.DivideByLength(local_div_l_b, True)[1:-1]

        pts_a = [a_crv.PointAt(t) for t in t_vals_a]
        local_other_part = [b_crv.PointAt(t) for t in t_vals_b]

        pln = rg.Plane(c_crv.PointAt(0.0), rg.Vector3d(0,0,1))

        # getting normals

        tmp_offset_crv_1 = c_crv.Offset(pln, 1.0, .01, rg.CurveOffsetCornerStyle.Round)[0]
        tmp_offset_crv_2 = c_crv.Offset(pln, -1.0, .01, rg.CurveOffsetCornerStyle.Round)[0]

        if tmp_offset_crv_1.GetLength() < tmp_offset_crv_2.GetLength():

            offset_crv = tmp_offset_crv_2
        
        else:

            offset_crv = tmp_offset_crv_1
        
        normals_a = [(pt - offset_crv.PointAt(offset_crv.ClosestPoint(pt)[1])) for pt in pts_a]
        normals_a = [n * (1.0 / rg.Point3d(0,0,0).DistanceTo(rg.Point3d(n))) for n in normals_a]

        loc_pattern_part = []

        for pt_i, pt in enumerate(pts_a):

            loc_pattern_part.append(Vertex(pt, normals_a[pt_i], x_val = pt_i * div_l, y_val = ref_i * lay_h))

        pattern_part.append(loc_pattern_part)
        other_part.append(local_other_part)

        offset_crvs.append(offset_crv)

    output_layers = [pattern_part, other_part]

    return output_layers, (crv_l, div_l, lay_h), offset_crvs