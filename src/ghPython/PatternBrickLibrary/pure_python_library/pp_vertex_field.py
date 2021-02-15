# pp vertex_field

from pp_vertex import *

class VertexField():

    def __init__(self, nested_v_list = []):

        if any(nested_v_list):
            self.v_set = []
            if isinstance(nested_v_list[0], list):
                [self.v_set.extend(v_list) for v_list in nested_v_list]
                self.nested = True

            elif isinstance(nested_v_list[0], Vertex):
                self.nested = False
                self.v_set = nested_v_list
            else:
                print("invalid input")

        self.m_function_set = False

    def set_mask(self, m_field):
        self.m_function_set = True
        self.m_function = m_field

    def bounding_box(self):
        

