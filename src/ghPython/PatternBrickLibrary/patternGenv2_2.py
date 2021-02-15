import Rhino.Geometry as rg
import math
import random
from vertexClass import Vertex
from copy import deepcopy as dc


# class Dot2D:

#     def __init__(self, location = None, direction = 1.0, radius = 5.0, n_max_val = 5.0, rot_alfa = None, xy_scale_vals = None, top_rad = None, bot_rad = None):

#         self.update_parameters(location, direction, radius, n_max_val, rot_alfa, xy_scale_vals, top_rad, bot_rad)

#     def update_parameters(self, location = None, direction = 1.0, radius = 5.0, n_max_val = 5.0, rot_alfa = None, xy_scale_vals = None, top_rad = None, bot_rad = None):

#         self.loc = location
#         self.dir = direction
#         self.r = radius
#         self.n_max_val = n_max_val

#         self.special = False
#         self.rot_scale = False
#         self.xy_scale = False

#         # dealing with cylinder 2dDotMaps

#         if bot_rad == None and top_rad == None:

#             self.top_rad = radius
#             self.bot_rad = radius

#         elif bot_rad == None:

#             self.top_rad = top_rad
#             self.bot_rad = top_rad

#         else:

#             self.top_rad = radius
#             self.bot_rad = top_rad

#         self.delta_r = self.top_rad - self.bot_rad

#         self.h = radius

#         if not(self.rot_scale == None):

#             self.special = True

#             self.rot_scale = True

#             self.rot_alfa = rot_alfa

#         if not(self.rot_scale == None):

#             self.special = True

#             self.xy_scale = True

#             self.x_scale, self.y_scale = xy_scale_vals

#             self.h = radius * self.y_scale

#         self.h_h = self.h * .5

#     def scale_input_pt(self, pt):

#         loc_pt = pt - self.loc

#         if self.xy_scale:

#             loc_pt = rg.Point3d(loc_pt.X * self.x_scale, loc_pt.Y * self.y_scale, 0.0)

#         if self.rot_scale:
            
#             rot_m = rg.Transform.Rotation(rg.Point3d(0,0,0), self.rot_alfa)

#             loc_pt.Transform(rot_m)

#         return loc_pt + self.loc

#     def get_distance(self, pt):

#         # saving the last distance into the instance, so it doesn't have to be recalcuated later

#         if self.special:

#             pt = self.scale_input_pt(pt)

#         self.rel_loc_pt = self.loc - pt
        
#         self.working_dis = 1.0 - self.loc.DistanceTo(pt) / self.r

#         if self.working_dis < 0.0:

#             self.working_dis = 0.0

#         return self.working_dis

# class PyramidDot2D(Dot2D):

#     @ property
#     def move_val(self):

#         # linear trajectory

#         return self.working_dis * self.dir * self.n_max_val

# class EllipsoidDot2D(Dot2D):

#     @ property
#     def move_val(self):

#         # ellipsoid trajectory

#         elliptical_remap = (1.0 - (self.working_dis / self.r) ** 2.0) ** .5

#         return elliptical_remap * self.n_max_val * self.dir * self.n_max_val

# class CylinderDot2D(Dot2D):

#     @ property
#     def move_val(self):

#         # this one is special

#         x_dis, y_dis = abs(self.rel_loc_pt.X), self.rel_loc_pt.Y

#         if abs(y_dis) < self.h_h:

#             local_r = self.bot_rad + self.delta_r * (y_dis / self.h_h)

#         else:

#             local_r = -1

#         if x_dis < local_r:

#             elliptical_remap = (1.0 - (x_dis / local_r) ** 2.0) ** .5

#             scale_val =  elliptical_remap * self.dir * self.n_max_val

#         else:

#             scale_val = 0.0

#         return scale_val

# class ConstraintRec:

#     def __init__(self, b_pt, x_l, y_l):

#         x_interval = rg.Interval(b_pt[0] - x_l * .5, b_pt[0] + x_l * .5)
#         y_interval = rg.Interval(b_pt[1] - y_l * .5, b_pt[1] + y_l * .5)

#         self.constraint = rg.Rectangle3d(rg.WorldXY, x_interval, y_interval)

#     def constraint_trimming(self, pt):

#         return self.constraint.Contains(pt) == rg.PointContainment.Inside

#     def constraint_radius(self, b_pt):

#         distances = [self.constraint.Corner[i].DistanceTo(b_pt) for i in range(4)]

#         return max(distances)


# class DotMap2D:

#     MAX_DOTS = 250

#     RND_SEED = 1

#     def __init__(self, spacing, constraint, spacing_y = None, rotation_angle = None, dot_type = PyramidDot2D()):

#         self.spacing = spacing
#         self.constraint = constraint

#         self.dot_type = dot_type
        
#         if spacing_y == None:

#             self.spacing_y = self.spacing
#             self.spacing_y_factor = 1.0

#         else:

#             self.spacing_y = spacing_y
#             self.spacing_y_factor = spacing_y / spacing

#         if rotation_angle == None:


#             self.rotate = False

#         else:

#             self.rotate = True
#             self.rot_a = rotation_angle

#         # def random values

#         self.rnd = False

#         self.rnd_culling = False
#         self.rnd_in_out = False
#         self.rnd_g_scaling = False
#         self.rnd_y_scaling = False
#         self.rnd_rotation = False
#         self.rnd_move = False

#         self.dots = []

#         random.seed(DotMap2D.RND_SEED)

#     def get_move(self, vertex):

#         distances = [dot.get_distance(vertex.loc) for dot in self.dots]

#         i = distances.index(min(distances) )

#         n_val = self.dots[i].move_val

#         vertex.warp_pt(n_val)

#     def random_settings(self, culling = False, cull_percentage = 0.0, random_in_out = False, percentage_in = .5, global_scale_random = False, global_scale_delta = 0.0, y_scale_random = False, y_scale_delta = .0, n_scale_random = False, n_scale_delta = 0.0, rotation_random = False, angle = .5, move_random = False, quantity = 0.0):

#         if culling or random_in_out or y_scale_random or rotation_random or move_random:

#             self.rnd = True

#             if culling:

#                 self.rnd_culling = True
#                 self.rnc_cull_percentage = cull_percentage

#             if random_in_out:

#                 self.rnd_in_out = True
#                 self.rnd_in_percentage = percentage_in

#             if global_scale_random:

#                 self.rnd_g_scaling = True
#                 self.rnd_g_scale = global_scale_delta

#             if y_scale_random:

#                 self.rnd_y_scaling = True
#                 self.rnd_y_scale = y_scale_delta

#             if n_scale_random:

#                 self.rnd_n_scaling = True
#                 self.rnd_n_scale = n_scale_delta

#             if rotation_random:

#                 self.rnd_rotation = True
#                 self.rnd_rot_angle = angle

#             if move_random:

#                 self.rnd_move = True
#                 self.rnd_move_dis = quantity

#     def random_f(self, pt):

#         add_pt = True
#         direction = 1.0
#         g_scaling = 1.0
#         y_scaling = 1.0
#         alfa = 0.0
#         move_vec = rg.Point3d(0,0,0)

#         if self.rnd_culling:

#             add_pt = random.random() > self.rnd_culling

#         if add_pt:

#             if self.rnd_in_out:

#                 if random.random() < self.rnd_in_percentage:

#                     direction = -1.0

#             if self.rnd_g_scaling:

#                 g_scaling = 1.0 + (random.random() * 2.0 - 1.0) * self.rnd_g_scale

#             if self.rnd_y_scaling:

#                 y_scaling = (1.0 + (random.random() * 2.0 - 1.0) * self.rnd_y_scale) * g_scaling

#             if self.rnd_n_scaling:

#                 n_scaling = 1.0 + (random.random() * 2.0 - 1.0) * self.rnd_n_scale

#             if self.rnd_rotation:

#                 alfa = (random.random() * 2.0 - 1.0) * self.rnd_rotation

#             if self.rnd_move:
                
#                 loc_alfa = random.random() * math.pi * 2.0
#                 radius = random.random() * self.rnd_move_dis

#                 move_vec = rg.Point3d(
#                     x = math.cos(loc_alfa) * radius,
#                     y = math.sin(loc_alfa) * radius,
#                     z = 0
#                 )

#         return add_pt, direction, (g_scaling, y_scaling), n_scaling, alfa, move_vec

#     def add_pt(self, pt):

#         add_pt = self.constraint.constraint_trimming(pt)
#         dot = dc(self.dot_type)

#         if self.rnd and add_pt:

#             add_pt, d, xy_sc, n_sc, alfa, move_vec = self.random_f(pt)

#             loc = pt + move_vec
#             direction = self.dot_type.dir * direction

#             r, b_r, t_r, n = dot.r, dot.bot_rad, dot.top_rad, dot.n_max_val

#             dot.update_parameters(loc, d, r, n * n_sc, alfa, xy_sc, t_r, b_r)

#         elif add_pt:

#             dot.loc = pt

#         if add_pt:

#             self.dots.append(dot)


# class RectangularDotMap(DotMap2D):

#     def make_dot_map(self, b_pt):

#         self.dots = []

#         pass

# class FibonacciSpiralDotMap(DotMap2D):

#     def make_dot_map(self, b_pt, start_angle = 0.0):

#         self.dots = []

#         i = 0
#         r = 0

#         add_pt = True

#         stop_r = self.constraint.constraint_radius(b_pt)

#         while i < DotMap2D.MAX_DOTS and r < stop_r:

#             r = self.spacing * math.sqrt(i)
#             theta = i * 2.4 + start_angle
            
#             pt = rg.Point3d(
#                 x = b_pt[0] + math.cos(theta) * r,
#                 y = b_pt[1] + math.sin(theta) * r,
#                 z = 0
#             )
        
#             self.add_pt(pt)

class PatternMap:

    DOT_MAP_RND = False
    DOT_MAP_RND_SEED = 0
    Y_SPACING_FACTOR = 1.0

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

            if not(direction):

                scale_val = - scale_val

            pt.warp_pt(scale_val)


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

        random.seed(PatternMap.DOT_MAP_RND_SEED)

        y_val = 0.0
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

        while y_val < self.height:

            if count % 2 == 1:

                x_val = x_spacing * .5

            else:

                x_val = 0.0

            while x_val < self.length + .1:

                loc_vertex = Vertex(x_val = x_val, y_val = y_val)

                if PatternMap.DOT_MAP_RND:
                    
                    multiplier = round(random.random()) * 2 - 1

                    loc_vertex.n_scale *= multiplier

                dots.append(loc_vertex)

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

            v_i = distance_set.index(distance)

            distance -= radius

            if distance < 0:

                scale_val = abs(distance) / radius * max_val

            else:

                scale_val = 0.0

            if not(direction):

                scale_val = - scale_val

            # using random values from dots
            
            scale_val *= dots[v_i].n_scale

            pt.warp_pt(scale_val)


    def ellipsoidBumpMap(self, spacing, radius, max_val, direction = True):

        dots = self.dotGen(spacing)

        for pt in self.surface_set:

            distance_set = []

            for dot in dots:

                distance = pt.numeric_distance(dot)
                distance_set.append(distance)

            distance = min(distance_set)

            v_i = distance_set.index(distance)

            if distance < radius:

                scale_val = (1 - (distance / radius) ** 2.0) ** .5 * max_val

            else:

                scale_val = 0.0

            if not(direction):

                scale_val = - scale_val

            # using random values from dots
            scale_val *= dots[v_i].n_scale

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

            # using random values from dots
            scale_val *= dot.n_scale

            pt.warp_pt(scale_val)


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
        pt_c = len(self.pts_set[:-1])

        # adding the vertices

        [srf_mesh.Vertices.Add(pt) for pt in self.pts_set[:-1]]

        for i in range(1, lay_c, 1):

            y = i - 1

            for pt_i, pt in enumerate(self.pts_set[:-1][i]):

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