import Rhino.Geometry as rg
import math
import random
from vertexClass import Vertex
from copy import deepcopy as dc

class PatternMap:

    DOT_MAP_UV_SHIFT=(0.0,0.0)
    DOT_MAP_SHIFT=False
    DOT_MAP_HARD_EASING=False
    DOT_MAP_RND=False
    DOT_MAP_RND_SEED=0
    Y_SPACING_FACTOR=1.0

    def __init__(self, layer_set, set_tuples, periodic = False, other_set = None):

        # set_tuples = (crv_l, div_l, lay_h)

        self.pattern_set = layer_set

        if not(other_set == None):

            self.add_other_set = True
            self.other_set = other_set

        else:
            
            self.add_other_set = False

        self.length, _, self.lay_h = set_tuples

        self.div_c = len(self.pattern_set[0])
        self.lay_c = len(self.pattern_set)

        self.height = self.lay_c * self.lay_h

        self.periodic = periodic

        self.closed = True
        self.curved = False

        self.rnd_inout = False
        self.rnd_cull = False
        self.rnd_radius = False
        self.rnd_n_val = False

        self.dir = 1.0
        
    def build(self):

        self.surface_set = []

        for pattern_layer in self.pattern_set:

            self.surface_set.extend(pattern_layer)

    def set_random_inout(self, percentage = .5, direction = 1.0):

        self.rnd_inout = True
        self.rnd_inout_percentage = percentage

    def random_inout(self):
        if self.rnd_inout_percentage < random.random():

            return -1.0

        else:

            return 1.0

    def set_random_cull(self, cull_val):

        self.rnd_cull = True
        self.rnd_cull_val = cull_val

    def set_random_radius(self, min_radius, max_radius):

        self.rnd_radius = True
        self.r_min, self.r_delta = min_radius, max_radius - min_radius

    def random_rad(self):

        return self.r_min + random.random() * self.r_delta

    def set_random_n_val(self, min_n_val, max_n_val):

        self.rnd_n_val = True
        self.n_min, self.n_delta = min_n_val, max_n_val - min_n_val

    def random_n_val(self):

        return self.n_min + random.random() * self.n_delta

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

        if self.periodic:

            print("sin periodicizing")
            print("updating the period")
            print("old period: %s" %period)

            period_count = math.ceil( self.length / ( 2 * math.pi * period ) )

            period = self.length / (period_count * 2 * math.pi)

            print("new period: %s" %period)

        for pt in self.surface_set:

            local_phase = pt.y_val / self.lay_h * phase_shift

            scale_val = math.sin(pt.x_val / period + local_phase) * amplitude

            pt.warp_pt(scale_val * self.dir)

    def patternGeneration(self, pattern_set, spacing):

        if self.periodic:

            print("pattern periodicizing")
            print("updating the spacing")
            print("old spacing: %s" %spacing)

            scaling_int_val = math.ceil(self.length / spacing)
            spacing = self.length / scaling_int_val

            print("new spacing: %s" %spacing)

        else:

            spacing = spacing

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

        if self.periodic:

            x_scale_val = 1.0
            y_scale_val = 1.0

        else:

            x_scale_val = 1.0
            y_scale_val = 1.0

        for pt in self.surface_set:

            # distance = pt.distance_function(x_spacing, y_spacing, layer_shift, rot_alfa, x_scale_val, y_scale_val)
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

            pt.warp_pt(scale_val * self.dir) 
    
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

            pt.warp_pt(scale_val * self.dir)


    def dotGen(self, spacing, y_spacing = None, feature_spacing=0.0):

        random.seed(PatternMap.DOT_MAP_RND_SEED)

        count = 0

        x_spacing = 2.0 ** .5 * spacing

        if self.periodic:

            print("dotGen periodicizing")
            print("updating the x_spacing")
            print("old x_spacing: %s" %x_spacing)

            x_spacing_int = math.ceil(self.length / (x_spacing * 2.0))
            x_spacing = (self.length / x_spacing_int) / 2.0

            print("new x_spacing: %s" %x_spacing)

        if y_spacing == None:

            y_spacing = x_spacing * PatternMap.Y_SPACING_FACTOR

        dots = []

        # setting the start and end conditions of the dot_map
        if PatternMap.DOT_MAP_SHIFT:
            # print("shifting the pattern in the code as well")
            x_shift=PatternMap.DOT_MAP_UV_SHIFT[0] % x_spacing
            y_shift=PatternMap.DOT_MAP_UV_SHIFT[1] % y_spacing
            x_start=x_shift if x_shift < .5 * x_spacing else x_shift-x_spacing
            y_start=y_shift if y_shift < .5 * y_spacing else y_shift-y_spacing
        else:
            x_start, y_start = 0.0, 0.0

        x_end, y_end=self.length + .5 * x_spacing, self.height + .5 * y_spacing

        if PatternMap.DOT_MAP_HARD_EASING:
            while (x_start < feature_spacing):
                x_start += x_spacing
            while (x_end > self.length - feature_spacing):
                x_end -= x_spacing

        x_val=x_start
        y_val=y_start

        while y_val < y_end:

            if count % 2 == 1:

                x_val = x_spacing * .5 + x_start

            else:

                x_val = x_start

            while x_val < x_end + .1:

                loc_vertex = Vertex(x_val = x_val, y_val = y_val)

                dots.append(loc_vertex)

                x_val += x_spacing

            y_val += y_spacing
            count += 1

        if self.rnd_cull:

            new_dots = []

            for dot in dots:

                if random.random() < self.rnd_cull_val:

                    new_dots.append(dot)

            dots = new_dots

        if self.rnd_inout:

            self.in_out_multi = [self.random_inout() for i in range(len(dots))]

        if self.rnd_radius:

            self.radii = [self.random_rad() for i in range(len(dots))]

        if self.rnd_n_val:

            self.n_vals = [self.random_n_val() for i in range(len(dots))]

        return dots

    def dotMap(self, spacing, radius, max_val, direction = None):

        dots = self.dotGen(spacing, feature_spacing=radius)

        for pt in self.surface_set:

            distance_set = []

            for dot in dots:

                distance = pt.numeric_distance(dot)
                distance_set.append(distance)

            distance = min(distance_set)

            v_i = distance_set.index(distance)

            if self.rnd_radius:

                radius = self.radii[v_i]

            if self.rnd_n_val:

                max_val = radius * self.n_vals[v_i]

            distance -= radius

            if distance < 0:

                scale_val = abs(distance) / radius * max_val

            else:

                scale_val = 0.0

            if self.rnd_inout:

                scale_val *= self.in_out_multi[v_i]

            pt.warp_pt(scale_val * self.dir)


    def ellipsoidBumpMap(self, spacing, radius, max_val, direction = None):

        dots = self.dotGen(spacing, feature_spacing=radius)

        for pt in self.surface_set:

            distance_set = []

            for dot in dots:

                distance = pt.numeric_distance(dot)
                distance_set.append(distance)

            distance = min(distance_set)

            v_i = distance_set.index(distance)

            if self.rnd_radius:

                radius = self.radii[v_i]

            if self.rnd_n_val:

                max_val = radius * self.n_vals[v_i]

            if distance < radius:

                scale_val = (1 - (distance / radius) ** 2.0) ** .5 * max_val

            else:

                scale_val = 0.0

            if self.rnd_inout:

                scale_val *= self.in_out_multi[v_i]

            pt.warp_pt(scale_val * self.dir)


    def getKey(self, item):

        return item[0]

    def cylinderMap(self, spacing, height, radius, max_val, radius_bot = None):

        radius_bot=radius if radius_bot == None else radius_bot

        radius_delta = radius - radius_bot
        
        radius_f = 1.0 - radius_delta / radius

        dots = self.dotGen(spacing, feature_spacing=max([radius, radius_bot]))

        for pt in self.surface_set:

            # get closest dot

            distance_set = []

            for dot in dots:

                distance = pt.numeric_distance(dot)
                distance_set.append((distance, dot))

            distance = min(distance_set)

            v_i = distance_set.index(distance)

            dot = dots[v_i]

            if self.rnd_radius:

                radius = self.radii[v_i]
                radius_bot = radius * radius_f

            if self.rnd_n_val:

                max_val = radius * self.n_vals[v_i]

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

            if self.rnd_inout:

                scale_val *= self.in_out_multi[v_i]

            pt.warp_pt(scale_val * self.dir)


    def makeCurves(self):

        self.pts_set = []
        crv_set = []

        for layer_i, layer_set in enumerate(self.pattern_set):

            pt_set = [vertex.v for vertex in layer_set]

            if self.add_other_set:

                pt_set = pt_set + self.other_set[layer_i][1:-1] + [pt_set[0]]

            if self.periodic:

                # print("I am giving you a closed polyline")

                pt_set = pt_set + [pt_set[0]]

            self.pts_set.append(pt_set)

            crv = rg.Polyline(pt_set)

            crv_set.append(crv)

        self.curved = True

        return crv_set


    def makeMesh(self, quad = False):

        if not(self.curved):

            self.makeCurves()

        srf_mesh = rg.Mesh()

        lay_c = len(self.pts_set)
        pt_c = len(self.pts_set[0][:-1])

        # adding the vertices

        [srf_mesh.Vertices.Add(pt) for pt in self.pts_set[0][:-1]]

        for i in range(1, lay_c, 1):

            y = i - 1

            for pt_i, pt in enumerate(self.pts_set[i][:-1]):

                x = pt_i

                srf_mesh.Vertices.Add(pt)

                v_a = y * pt_c + (x - 1)%pt_c
                v_b = (y + 1) * pt_c + (x - 1)%pt_c
                v_c = (y + 1) * pt_c + x
                v_d = y * pt_c + x

                if quad:

                    srf_mesh.Faces.AddFace(v_a, v_b, v_c, v_d)

                else:

                    srf_mesh.Faces.AddFace(v_a, v_b, v_d)
                    srf_mesh.Faces.AddFace(v_b, v_c, v_d)


        # addding the faces

        return srf_mesh