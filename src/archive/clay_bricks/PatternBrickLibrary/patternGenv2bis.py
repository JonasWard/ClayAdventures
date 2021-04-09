import Rhino.Geometry as rg
import math
from vertexClass import Vertex


class DotMap(object):

    def __init__(self, spacing, spacing_y = None, dot_gen_pattern_type = "rectangle", rotation_angle = None, random_culling = 0.0):

        self.spacing = spacing
        
        if spacing_y == None:

            self.spacing_y = self.spacing

        else:

            self.spacing_y = spacing_y

        if rotation_angle == None:

            self.rotate = False

        else:

            self.rotate = True
            self.rot_a = rotation_angle

        if random_culling > .01:

            self.rnd_cull = True
            self.rnd_cull_tresh = random_culling
        

class PatternMap(object):

    def __init__(self, layer_sets, set_tuples, periodic = False):

        # set_tuples = (crv_l, div_l, lay_h)

        self.pattern_set, self.normal_set = layer_sets[0], layer_sets[1]

        # print(self.pattern_set)

        self.length, _, self.lay_h = set_tuples

        self.div_c = len(self.pattern_set[0]) + len(self.normal_set[0]) + 1
        self.lay_c = len(self.normal_set)

        self.height = self.lay_c * self.lay_h

        self.periodic = periodic

        
    def build(self):

        self.surface_set = []

        for pattern_layer in self.pattern_set:

            self.surface_set.extend(pattern_layer)


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

    def modBasedDotMap(self, x_spacing = 20.0, y_spacing = 20.0, max_val = 10.0, ellipsoid = True, direction = True, layer_shift = 2.0, shift_a = 0.0, shift_b = 0.0, rot_alfa = 0.0):

        for pt in self.surface_set:

            distance = pt.distance_function(x_spacing, y_spacing, layer_shift, rot_alfa)

            # applying shift values if necessary
            if not(shift_a == 0.0):

                distance *= shift_a

            if not(shift_b == 0.0):

                distance += shift_b

            # curtaling the distances
            if distance < 0.0:

                scale_val = 0.0

            elif distance > 1.0:

                scale_val = max_val

            else:

                if ellipsoid:

                    distance = (1 - (1 - distance) ** 2.0) ** .5

                scale_val = max_val * distance

            if not(direction):

                scale_val = - scale_val

            pt.warp_pt(scale_val) 
    
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

        self.pts_set = []
        crv_set = []

        for layer_i, layer_set in enumerate(self.pattern_set):

            pt_set = [vertex.v for vertex in layer_set]
            pt_set = pt_set + self.normal_set[layer_i] + [pt_set[0]]

            self.pts_set.append(pt_set)

            crv = rg.Polyline(pt_set)

            crv_set.append(crv)

        return crv_set


    def makeMesh(self):

        self.makeCurves()

        surface_mesh = rg.Mesh()

        # adding the vertices

        for pts in self.pts_set:

            for pt in pts:

                surface_mesh.Vertices.Add(pt)

        # addding the faces

        for y in range(self.lay_c - 1):

            for x in range(self.div_c):

                v_a = y * self.div_c + x -1
                v_b = (y + 1) * self.div_c + x -1
                v_c = (y + 1) * self.div_c + x
                v_d = y * self.div_c + x

                # quad mesh
                surface_mesh.Faces.AddFace(v_a, v_b, v_c, v_d)

                # # tri mesh
                # surface_mesh.Faces.AddFace(v_a, v_b, v_c)
                # surface_mesh.Faces.AddFace(v_c, v_d, v_a)

        return surface_mesh