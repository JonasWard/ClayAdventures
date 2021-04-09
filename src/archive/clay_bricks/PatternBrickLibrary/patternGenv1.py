import Rhino.Geometry as rg
import math

# grasshoppper variables

# geometric variables
base_crv
origin
sub_length
layer_count
layer_height

# pattern variables
period
phase_shift

# pattern generation
edge_easing
edge_ease_zero
edge_ease_end

pattern_type

period
phase_shift

spacing
radius
max_val

height
radius_bot

direction


class Vertex(object):

    def __init__(self, pt = rg.Point3d(0,0,0), normal = rg.Point3d(1,0,0), x_val = 0, y_val = 0):

        self.o = pt
        self.v = pt
        
        self.n = normal
        self.n_scale = 1.0

        self.x_val = x_val
        self.y_val = y_val


    def numeric_distance(self, other):

        return ((self.x_val - other.x_val) ** 2 + (self.y_val - other.y_val) ** 2) ** .5


    def x_distance(self, other):

        return abs(self.x_val - other.x_val)


    def move_pt(self, mv_pt):

        return Vertex(self.o + mv_pt, self.n, self.x_val, self.y_val)
        

    def warp_pt(self, scale_val = 0):

        self.v = rg.Point3d(self.o + self.n * (scale_val * self.n_scale))


class PatternMap(object):

    def __init__(self, base_crv, origin = rg.Point3d(0,0,0)):

        self.base_crv = base_crv


    def subdivide(self, div_length):

        self.length = self.base_crv.GetLength()
        div_c = int(self.length / div_length)
        self.div_length = self.length / div_c
        self.div_c = div_c + 1
        
        t_vals = self.base_crv.DivideByLength(self.div_length, True)

        pts = [self.base_crv.PointAt(t) for t in t_vals]

        # getting normals

        tmp_offset_crv_1 = self.base_crv.Offset(rg.Plane.WorldXY, 1.0, .01, rg.CurveOffsetCornerStyle.Sharp)[0]
        tmp_offset_crv_2 = self.base_crv.Offset(rg.Plane.WorldXY, -1.0, .01, rg.CurveOffsetCornerStyle.Sharp)[0]

        if tmp_offset_crv_1.GetLength() < tmp_offset_crv_2.GetLength():

            offset_crv = tmp_offset_crv_2
        
        else:

            offset_crv = tmp_offset_crv_1
        
        normals = [(pt - offset_crv.PointAt(offset_crv.ClosestPoint(pt)[1])) for pt in pts]

        self.base_layer = []

        for pt_i, pt in enumerate(pts):

            self.base_layer.append(Vertex(pt, normals[pt_i], x_val = pt_i * self.div_length))


    def generate(self, layer_height, layer_count):

        self.lay_h = layer_height
        self.lay_c = layer_count

        self.height = self.lay_h * self.lay_c

        self.surface_set = []

        for z_in in range(self.lay_c):

            z_val = z_in * self.lay_h

            z_mv_pt = rg.Point3d(0, 0, z_val)

            local_layer = []

            for pt in self.base_layer:
                
                tmp_new_pt = pt.move_pt(z_mv_pt)
                tmp_new_pt.y_val = z_val

                local_layer.append(tmp_new_pt)

            self.surface_set.extend(local_layer)

    def edgeEasing(self, zero_length, normal_length):

        ease_delta = normal_length - zero_length

        for pt in self.surface_set:

            if pt.x_val < zero_length or pt.x_val > self.length - zero_length:

                pt.n_scale = 0.0

            elif pt.x_val < normal_length:

                pt.n_scale = abs(pt.x_val - zero_length) / ease_delta
                
            elif pt.x_val > self.length - normal_length:

                pt.n_scale = abs(pt.x_val - (self.length - zero_length)) / ease_delta


    def sinWarp(self, period, amplitude, phase_shift, direction = True):

        for pt in self.surface_set:

            local_phase = pt.y_val / self.lay_h * phase_shift

            scale_val = math.sin(pt.x_val / period + local_phase) * amplitude

            if not(direction):

                scale_val = - scale_val

            pt.warp_pt(scale_val)


    def patternGeneration(self, pattern_set, spacing):

        # pattern_map (start, step, count)
        # only have to consider x distance

        layer_set = []
        layer_count = 0
        layer_length_vals = []

        for pattern in pattern_set:

            start, step, count = pattern[0], pattern[1], pattern[2]

            if count < 1:

                count = 1

            layer_vertexes = []
            length_vals = []
            
            x_val = start

            x_delta = step * spacing

            while x_val < self.length:

                layer_vertexes.append(Vertex(x_val = x_val))
                length_vals.append(x_val)

                x_val += x_delta

            for i in range(count):

                layer_set.append(layer_vertexes)
                layer_length_vals.append(length_vals)

            layer_count += count

        return layer_set, layer_length_vals, layer_count

    def curveSplitAtPoints(self, radius, length_vals):

        pass


    def specialLayerMap(self, spacing, pattern_set, radius, max_val, direction = True):

        _, layer_length_vals, layer_count = self.patternGeneration(pattern_set, spacing)

        

    
    def layerMap(self, spacing, pattern_set, radius, max_val, direction = True):

        # pattern_map (start, step, count)
        # only have to consider x distance

        layer_set, _, layer_count = self.patternGeneration(pattern_set, spacing)

        # subdividing in layers
        for pt_i, pt in enumerate(self.surface_set):

            layer_index = (pt_i - pt_i % self.div_c) / self.div_c

            pattern_layer_index = int(layer_index % layer_count)

            dots = layer_set[pattern_layer_index]

            dis_set = []

            for dot in dots:

                dis_set.append(pt.x_distance(dot))

            distance = min(dis_set)

            if distance < radius:

                scale_val = (1 - (distance / radius) ** 2.0) ** .5 * max_val

            else:

                scale_val = 0.0

            if not(direction):

                scale_val = - scale_val

            pt.warp_pt(scale_val)


    def dotGen(self, spacing, y_spacing = None):

        y_val = 0.0
        count = 0

        x_spacing = 2.0 ** .5 * spacing

        if y_spacing == None:

            y_spacing = x_spacing * .5

        dots = []

        while y_val < self.height:

            if count % 2 == 1:

                x_val = x_spacing * .5

            else:

                x_val = 0.0

            while x_val < self.length:

                print(x_val, y_val)

                dots.append(Vertex(x_val = x_val, y_val = y_val))

                x_val += x_spacing

            y_val += y_spacing
            count += 1

        return dots


    def dotMap(self, spacing, radius, max_val, direction = True):

        dots = self.dotGen(spacing)

        for pt in self.surface_set:

            distance_set = []

            for dot in dots:

                distance = pt.numeric_distance(dot)
                distance_set.append(distance)

            distance = min(distance_set)

            distance -= radius

            if distance < 0:

                scale_val = abs(distance) / radius * max_val

            else:

                scale_val = 0.0

            if not(direction):

                scale_val = - scale_val

            pt.warp_pt(scale_val)


    def ellipsoidBumpMap(self, spacing, radius, max_val, direction = True):

        dots = self.dotGen(spacing)

        for pt in self.surface_set:

            distance_set = []

            for dot in dots:

                distance = pt.numeric_distance(dot)
                distance_set.append(distance)

            distance = min(distance_set)

            if distance < radius:

                scale_val = (1 - (distance / radius) ** 2.0) ** .5 * max_val

            else:

                scale_val = 0.0

            if not(direction):

                scale_val = - scale_val

            pt.warp_pt(scale_val)


    def getKey(self, item):

        return item[0]


    def cylinderMap(self, spacing, height, radius, max_val, radius_bot = None, direction = True):

        if radius_bot == None:

            radius_bot = radius
            radius_delta = 0

        else:

            radius_delta = radius - radius_bot

        dots = self.dotGen(spacing)

        for pt in self.surface_set:

            # get closest dot

            distance_set = []

            for dot in dots:

                distance = pt.numeric_distance(dot)
                distance_set.append((distance, dot))

            _, dot = sorted(distance_set, key = self.getKey)[0]

            print(dot)

            # y_distance calculation

            y_distance = pt.y_val - dot.y_val

            # x_distance calculation

            x_distance = abs(pt.x_val - dot.x_val)

            if abs(y_distance) + .01 < height * .5 :

                local_radius = radius_bot + radius_delta * (y_distance / height + .5)

            else:

                local_radius = -1

            if x_distance < local_radius:

                scale_val = (1 - (x_distance / local_radius) ** 2.0) ** .5 * max_val

            else:

                scale_val = 0.0

            if not(direction):

                scale_val = - scale_val

            pt.warp_pt(scale_val)


    def makeCurves(self):

        curve_set = []
        pt_set = []

        for pt_in, pt in enumerate(self.surface_set):

            pt_set.append(pt.v)

            if pt_in % self.div_c == self.div_c - 1:

                crv = rg.Polyline(pt_set).ToNurbsCurve()

                curve_set.append(crv)

                pt_set = []

        return curve_set


    def makeMesh(self):

        surface_mesh = rg.Mesh()

        # adding the vertices

        for pt in self.surface_set:

            surface_mesh.Vertices.Add(pt.v)

        # addding the faces

        for y in range(self.lay_c - 1):

            for x in range(self.div_c - 1):

                v_a = y * self.div_c + x
                v_b = (y + 1) * self.div_c + x
                v_c = (y + 1) * self.div_c + x + 1
                v_d = y * self.div_c + x + 1

                surface_mesh.Faces.AddFace(v_a, v_b, v_c, v_d)

        return surface_mesh



pattern_map = PatternMap(base_crv, origin)
pattern_map.subdivide(sub_length)
pattern_map.generate(layer_height, layer_count)

if edge_easing:

    pattern_map.edgeEasing(edge_ease_zero, edge_ease_end)

if pattern_type == 0:
    
    pattern_map.dotMap(spacing, radius, max_val, direction)

elif pattern_type == 1:

    pattern_map.ellipsoidBumpMap(spacing, radius, max_val, direction)

elif pattern_type == 2:

    pattern_map.sinWarp(period, max_val, phase_shift, direction)

elif pattern_type == 3:

    if radius_bot < .01:

        radius_bot = radius

    else:

        radius_bot = radius_bot

    pattern_map.cylinderMap(spacing, height, radius, max_val, radius_bot, direction)

elif pattern_type == 4:

    pattern_map.layerMap(spacing, pattern_set, radius, max_val, direction)


c = pattern_map.makeMesh()
b = pattern_map.makeCurves()

