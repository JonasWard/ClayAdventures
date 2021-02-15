import math

class NoneFunction():
    def get_val(self, _=None):
        return 1.0

class SimpleSine():
    def __init__(self, period_x=1.0, period_y=None, period_z=None, amplitude = 0.0, warp=None):
        self.p_x=period_x
        self.a=amplitude
        if period_y == None:
            self.v_attribute="1D"
        else:
            self.p_y=period_y
            self.v_attribute="2D"

        if not(period_y is None) and not(period_z is None):
            self.v_attribute="3D"
            self.p_z=period_z

    def get_val(self, vertex):
        if self.v_attribute=="1D":
            return math.sin(vertex.numeric1D / self.p_x) * self.a
        elif self.v_attribute=="2D":
            u, v = vertex.numeric2D.tuples
            return math.sin(u / self.p_x + v / self.p_y) * self.a
        elif self.v_attribute=="3D":
            x, y, z = vertex.numeric3D
            return math.sin(x / self.p_x + y / self.p_y + z / self.p_z) * self.a
