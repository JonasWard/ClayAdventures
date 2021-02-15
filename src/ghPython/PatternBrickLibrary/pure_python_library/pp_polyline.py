# pure_python vertex polyline
# this class will only be used when doing layer operations - collapses
# and linear growth algorithms

from pp_vertex import Vertex
from pp_vector import Vector3D
from math import tan
class LineSegement():

    def __init__(self, v_0, v_1):
        self.start = v_0
        self.end = v_1

    @property
    def tangent_vec(self):
        return self.end.c - self.start.c

    @property
    def normal_vec(self):
        return self.tangent_vec.normal2D()

    @property
    def numeric_delta(self):    
        return self.end.n_v - self.start.n_v

    @property
    def index_delta(self):
        return self.end.index - self.start.index

    @property
    def length(self):
        return self.start.distance(self.end)

    def regrading_index_values(self, new_vertexes):
        v_list = [self.start] + new_vertexes + [self.end]
        partial_sums = []
        total_length = 0.0

        for i in range(len(v_list - 1)):
            total_length += v_list[i].distance(v_list[i + 1] )
            partial_sums.append(total_length)

        for i, n_v in enumerate(new_vertexes):
            n_v.index = self.start.index + partial_sums[i] / total_length * self.index_delta

    def interpolate(self, value):
        return Vertex(
            location = self.start.c + self.tangent_vec * value,
            normal = self.normal_vec,
            index = self.start.index + self.index_delta * value
        )

    def split(self, *values):
        return [self.interpolate(val) for val in values]

    def add_triangle(self, width, height, shift_top = None, mid_val = .5):
        # initializing new points
        t_l = self._dis_to_t_val(width) * mid_val
        t_vals = [mid_val - t_l, mid_val, mid_val + t_l]
        vec_list = self.split(t_vals)

        # actual movement
        if shift_top == None:
            vec_list[1].move_normal(height)
        else:
            vec_list[1].move_hook(height, shift_top)

        self.regrading_index_values(vec_list)

        return vec_list

    def add_trapazoid(self, start_width, height, end_width = None, end_shift = None, mid_val = .5):
        # initializing new points
        t_l = self._dis_to_t_val(start_width) * mid_val
        t_vals = [mid_val - t_l, mid_val - t_l, mid_val + t_l, mid_val + t_l]
        vec_list = self.split(t_vals)

        # actual movement
        if end_width == None and end_shift == None:
            vec_list[1].move_normal(height)
            vec_list[2].move_normal(height)
        
        else:
            m_1 = end_width * -.5
            m_2 = end_width * .5
            if not(end_shift == None):
                m_1 += end_shift
                m_2 += end_shift

            vec_list[1].move_hook(height, m_1)
            vec_list[2].move_hook(height, m_2)

        self.regrading_index_values(vec_list)

        return vec_list

    def _dis_to_t_val(self, dis):
        return dis / self.length * self.index_delta

class Polyline():
    N_MODE="simple" # simple : average preceding and next segment, complex tangent

    def __init__(self, vertex_list, closed = True):

        self.c = closed

        if len(vertex_list) < 2:
            print("You have to input at least 2 vertexes per polyline")

            return None

        if isinstance(vertex_list[0], Vertex):
            self.vs = vertex_list
            self._closed_check()

        elif isinstance(vertex_list[0], Vector3D):
            self.vs = [Vertex(pt) for pt in vertex_list]
            self._closed_check()
            self.construct_normals()

        self.lines_constructed = False

    @property
    def count(self):
        return len(self.vs)

    @property
    def _c_int(self):
        return int(not(self.c))

    @property
    def line_segments(self):
        if not(self.lines_constructed):
            self.construct_line_segments()
        return self._ln_s

    def _closed_check(self):
        if self.vs[0] == self.vs[-1]:
            self.c = True
            self.vs.pop(-1)

    def construct_normals(self):
        if not(self.c):
            self.vs[0].normal = self.lines_constructed[0].normal_vec
            self.vs[-1].normal = self.lines_constructed[-1].normal_vec

        if Polyline.N_MODE == "simple":
            for i in range(self._c_int - 1, self.count - self._c_int, 1):
                n_0 = self.lines_constructed[i].normal_vec
                n_1 = self.lines_constructed[(i + 1)%self.count].normal_vec
                self.vs[i + 1].normal = (n_0 + n_1) * .5

        if Polyline.N_MODE == "complex":
            for i in range(self._c_int - 1, self.count - self._c_int, 1):
                n_0 = self.lines_constructed[i].normal_vec
                n_1 = self.lines_constructed[(i + 1)%self.count].normal_vec
                n_mag = (1.0 - tan(n_0.angle_vec(n_1) * .5) ** 2.0) ** .5
                self.vs[i + 1].normal = (n_0 + n_1) * .5 * n_mag

    def construct_line_segments(self):
        self.lines_constructed = True
        self._ln_s = []

        for i in range(self.count - self._c_int):           # if self.c(closed) will have count, otherwise count - 1
            self._ln_s.append(LineSegement(self.vs[i], self.vs[(i + 1)%self.count]))
    
    def add_copy(self, mv_vs=[], z_shift=None):
        loc_vs = [v.add(mv_vs[i%len(mv_vs), z_shift]) for i, v in enumerate(self.vs)]
        return Polyline(loc_vs, self.c)

    def split(self, index):
        pass