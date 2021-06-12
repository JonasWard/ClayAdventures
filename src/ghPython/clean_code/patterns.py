# simple pattern class objects
# a pattern is a function that is applied to a vertex
# a vertex is defined as a point location and a normal
from math import sin, pi, ceil
import random
import Rhino.Geometry as rg

class Pattern():
    def apply(self, v):
        return v

class InOut():
    def __init__(self, percentage, seed = 0):
        self.p = percentage

        random.seed(seed)
        self.seed_dict = {}

    def get_direction(self, index):
        try:
            self.seed_dict[index]
        except:
            self.seed_dict[index] = random.random() < self.p

        return self.seed_dict[index]

class DotMap():
    def __init__(self, x_spacing = 10., y_spacing = None, half_spacing = False, b_pt = rg.Point3d.Origin, in_out_class = None, direction = True):
        self.x_spacing = x_spacing
        self.y_spacing = y_spacing
        self.o = b_pt
        self._h_spacing = half_spacing
        self.h_spacing_x = x_spacing * .5
        self.h_spacing_y = self.y_spacing * .5

        self.direction = direction

        self._random_function = in_out_class

        print(self._h_spacing)

    def position_based(self, pt):
        loc_pt = pt - self.o

        if self._h_spacing:
            p_x = loc_pt.X % self.x_spacing
            p_y = loc_pt.Y % self.y_spacing

            y_i = int((loc_pt.Y - p_y) / self.y_spacing)

            if y_i % 2 == 0:
                p_x += self.h_spacing_x
                p_x %= self.x_spacing

        else:
            p_x = loc_pt.X % self.x_spacing
            p_y = loc_pt.Y % self.y_spacing

            y_i = int((loc_pt.Y - p_y) / self.y_spacing)

        output_pt = rg.Point3d(
            p_x - self.h_spacing_x,
            p_y - self.h_spacing_y,
            0.
        )

        if not(isinstance(self._random_function, type(None))):
            x_i = int((loc_pt.X - p_x) / self.x_spacing)

            seed_val = x_i + y_i * 100
            direction = self._random_function.get_direction(seed_val)
        else:
            direction = True

        direction = direction if self.direction else not(direction)
        if direction:
            return output_pt, 1.
        else:
            return output_pt, -1.


class EdgeEasing():
    def __init__(self, zero_length, normal_length, total_length):
        self.min = zero_length
        self.max = normal_length
        self.d = self.max - self.min

        self.h_length = .5 * total_length

    def scale_val(self, d_x):
        d_x = self.h_length - abs(d_x - self.h_length)

        if d_x >= self.max:
            return 1.0
        elif d_x > self.min:
            return (d_x - self.min) / self.d
        else:
            return 0.


class SinWave(Pattern):
    def __init__(self, period, amplitude, dir_angle, b_pt = rg.Point3d.Origin, edge_easing = None):

        self.p = period * .5 / pi
        self.a = amplitude
        self.t_m = rg.Transform.Rotation(dir_angle, rg.Point3d.Origin)
        self.b_pt = b_pt

        self.ee = edge_easing

        print(self.ee)

    def apply(self, v):

        tmp_pt = v.vec_version - self.b_pt
        tmp_pt.Transform(self.t_m)

        if not(isinstance(self.ee, type(None))):
            amp = self.a * self.ee.scale_val(v.vec_version.X)
        else:
            amp = self.a

        scale_val = sin(tmp_pt.X / self.p) * amp
        return rg.Point3d(v.o + v.n * scale_val)


class PyramidPattern(Pattern):
    def __init__(self, radius, amplitude, y_scale = 1., dot_map = None, edge_easing = None):

        self.r = radius
        self.a = amplitude
        self.y_scale = y_scale
        self.dot_map = DotMap if isinstance(dot_map, type(None)) else dot_map

        self.ee = edge_easing

        print(self.ee)

    def apply(self, v):

        loc, direction = self.dot_map.position_based(v.vec_version)
        l = (loc.X ** 2. + (loc.Y * self.y_scale) ** 2.) ** .5

        if not(isinstance(self.ee, type(None))):
            amp = self.a * self.ee.scale_val(v.vec_version.X)
        else:
            amp = self.a

        if l > self.r:
            return v.v
        else:
            scale_val = direction * amp * (1. - l/self.r)

            return rg.Point3d(v.o + v.n * scale_val)


class EllipsoidPattern(Pattern):
    def __init__(self, radius, amplitude, y_scale=1., dot_map=None, edge_easing=None):

        self.r = radius
        self.a = amplitude
        self.y_scale = y_scale
        self.dot_map = DotMap if isinstance(dot_map, type(None)) else dot_map

        self.ee = edge_easing

        print(self.ee)

    def apply(self, v):

        loc, direction = self.dot_map.position_based(v.vec_version)
        l = (loc.X ** 2. + (loc.Y * self.y_scale) ** 2.) ** .5

        if not(isinstance(self.ee, type(None))):
            amp = self.a * self.ee.scale_val(v.vec_version.X)
        else:
            amp = self.a

        if l > self.r:
            return v.v
        else:
            h = (1 - (l / self.r) ** 2.) ** .5
            scale_val = direction * amp * h

            return rg.Point3d(v.o + v.n * scale_val)


class CylinderPattern(Pattern):
    def __init__(self, radius_a, radius_b, height, amplitude, dot_map=None, edge_easing=None):

        self.r_a = radius_a
        self.r_b = radius_b
        self.r_d = self.r_b - self.r_a
        self.r_f = self.r_d / self.r_a

        self.h = height

        self.a = amplitude
        self.dot_map = DotMap if isinstance(dot_map, type(None)) else dot_map

        self.ee = edge_easing

        print(self.ee)

    def apply(self, v):

        loc, direction = self.dot_map.position_based(v.vec_version)

        if not(isinstance(self.ee, type(None))):
            amp = self.a * self.ee.scale_val(v.vec_version.X)
        else:
            amp = self.a

        y_distance = loc.Y
        x_distance = abs(loc.X)

        if abs(y_distance) + .01 < self.h * .5:
            local_radius = self.r_a + self.r_d * (y_distance / self.h + .5)

        else:
            local_radius = -1

        if x_distance < local_radius:
            scale_val = (1 - (x_distance / local_radius) ** 2.0) ** .5 * amp * direction
            return rg.Point3d(v.o + v.n * scale_val)
        else:
            return v.v


class LayerMap(Pattern):
    def __init__(self, spacing, pattern_set, length, layer_spacing, radius, amplitude, direction = False, periodic = False, b_pt = rg.Point3d.Origin, edge_easing=None):
        self.periodic = periodic
        self.pattern_generation(pattern_set, spacing, length)

        self.l = length
        self.l_h = layer_spacing
        self.r = radius
        self.a = amplitude if direction else -amplitude
        self.b_pt = b_pt

        self.ee = edge_easing

    def pattern_generation(self, pattern_set, spacing, length):

        if self.periodic:

            print("pattern periodicizing")
            print("updating the spacing")
            print("old spacing: %s" % spacing)

            scaling_int_val = ceil(length / spacing)
            spacing = length / scaling_int_val

            print("new spacing: %s" % spacing)

        else:

            spacing = spacing

        # pattern_map (start, step, count)
        # only have to consider x distance

        layer_length_vals = []

        for pattern in pattern_set:

            start, step, count = pattern[0], pattern[1], pattern[2]

            if count < 1:
                count = 1

            length_vals = []

            x_val = start

            x_delta = step * spacing

            while x_val < length:
                length_vals.append(x_val)

                x_val += x_delta

            for i in range(count):
                layer_length_vals.append(length_vals)

        self.layer_length_vals = layer_length_vals

    def apply(self, v):

        tmp_pt = v.vec_version - self.b_pt
        d_x = tmp_pt.X % self.l

        i = int(tmp_pt.Y / self.l_h)

        x_diss = self.layer_length_vals[ i % len(self.layer_length_vals) ]

        dis_set = []

        for x_d in x_diss:
            dis_set.append(abs(d_x - x_d))

        distance = min(dis_set)

        if not (isinstance(self.ee, type(None))):
            amp = self.a * self.ee.scale_val(d_x)
        else:
            amp = self.a

        if distance < self.r:

            scale_val = (1 - (distance / self.r) ** 2.0) ** .5 * amp

        else:

            scale_val = 0.0

        return rg.Point3d(v.o + v.n * scale_val)

class AxolotlFlat(Pattern):
    def __init__(self, sdf, amplitude, direction = False, b_pt = rg.Point3d.Origin, edge_easing=None):

        self.sdf = sdf
        self.a = amplitude if direction else -amplitude
        self.b_pt = b_pt

        self.ee = edge_easing

    def apply(self, v):

        tmp_pt = v.vec_version - self.b_pt

        if not (isinstance(self.ee, type(None))):
            amp = self.a * self.ee.scale_val(v.vec_version.X)
        else:
            amp = self.a

        scale_val = self.sdf.GetDistance(tmp_pt.X, tmp_pt.Y, tmp_pt.Z) * amp
        return rg.Point3d(v.o + v.n * scale_val)


class AxolotlSpatial(Pattern):
    def __init__(self, sdf, amplitude, direction=False, b_pt=rg.Point3d.Origin, edge_easing=None):

        self.sdf = sdf
        self.a = amplitude if direction else -amplitude
        self.b_pt = b_pt

        self.ee = edge_easing

    def apply(self, v):

        tmp_pt = v.o - self.b_pt

        if not (isinstance(self.ee, type(None))):
            amp = self.a * self.ee.scale_val(v.vec_version.X)
        else:
            amp = self.a

        scale_val = self.sdf.GetDistance(tmp_pt.X, tmp_pt.Y, tmp_pt.Z) * amp
        return rg.Point3d(v.o + v.n * scale_val)