from pp_vector import Vector2D, Vector3D
from pp_distance_functions import NoneFunction

class Mask():

    def __init__(self, dimension=2):
        self.dimension=2
        self._flags={"default":NoneFunction()}

    def add_flag(self, flag_name, distance_object):
        self._flags[flag_name]=distance_object

    def get_val(self, location, flag=None):
        if flag is None or not(flag in self._flags):
            return self._flags["default"].get_val(location)
        else:
            return self._flags[flag].get_val(location)
