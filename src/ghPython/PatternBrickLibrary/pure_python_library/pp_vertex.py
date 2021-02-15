# pure python vertex class
# a vector object in this context is a container describing a
# physical location, an abstract location, a movement variable 
# and perhaps even a color vector. It is extended with some 
# scaling variables indicating whether you need to run it

from pp_vector import Vector3D, Vector2D
from pp_distance_functions import NoneFunction
# from pp_mask import Mask

class Vertex():
    Z_HASH = True
    TOL = .000001

    def __init__(self, location, normal=None, tangent=None, perpendicular=None, index=0.0, num_2D=None):
        """Pure Python Vertex Class, which consists of a pattern vertex

        Keyword args:
        location            int/float, tuple/list, Vector3D
        normal              int/float, tuple/list, Vector3D
        numeric_vec         int/float, tuple/list, Vector3D or None (default)
        """

        self._n=None
        self._t=None
        self._p=None

        self.c = Vector3D(location)     # c for current location
        self.o = Vector3D(location)     # o for original location

        # setting the normal values
        self.n_2D=False
        self.normal=normal
        self.tangent=tangent
        self.perpendicular=perpendicular

        # setting the locations for different functions
        self.numeric1D=index           
        self.numeric2D=num_2D

        # setting the mask
        self._mask={"default":NoneFunction()}

        # setting the hash
        self._hash=None
    
    # ==================== location values =================== #

    @property
    def x(self):
        return self.c.x

    @property
    def y(self):
        return self.c.y

    @property
    def z(self):
        return self.c.z

    @property
    def tuples(self):
        return self.c.tuples

    # =================== direction vectors ================== #
    @property
    def normal(self):
        return self._n
    
    @normal.setter
    def normal(self, vector):
        if isinstance(vector, Vector3D):
            self._n=vector
        elif isinstance(vector, Vector2D):
            self.n_2D=True
            self._n=vector
        else:
            print("default normal vector set")
            self._n=Vector3D(1,0,0)
    
    @property
    def tangent(self):
        return self._t
    
    @tangent.setter
    def tangent(self, vector):
        if isinstance(vector, Vector3D):
            self._t=vector
        elif isinstance(vector, Vector2D):
            self.n_2D=True
            self._t=vector
        elif vector is None:
            self._t=self.normal.perpendicular()
        else:
            print("default tangent vector set")
            self._t=Vector3D(0,1,0)

    @property
    def perpendicular(self):
        if not(self.n_2D):
            return self._p
        else:
            return Vector3D(0,0,0)
    
    @perpendicular.setter
    def perpendicular(self, vector):
        if isinstance(vector, Vector3D):
            self._p=vector
        elif isinstance(vector, Vector2D):
            self.n_2D=True
            self._p=vector
        elif vector is None:
            self._p=self.normal.perpendicular()
        else:
            print("default perpendicular vector set")
            self._p=Vector3D(0,0,1)

    # ==================== numeric values ==================== #
    @property
    def index(self):
        return self._num_1D

    @property
    def numeric1D(self):
        return self._num_1D
    @numeric1D.setter
    def numeric1D(self, val):
        if isinstance(val, float) or isinstance(val, int):
            self._num_1D=val
        elif val is None:
            self._num_1D=None
        else:
            print("invalid input for numeric1D {}".format(val))

    @property
    def numeric2D(self):
        return self._num_2D.tuples
    @numeric2D.setter
    def numeric2D(self, val):
        if val is None:
            self._num_2D=Vector2D(self.o.x, self.o.z)
        elif isinstance(val, tuple) or isinstance(val, int):
            if len(val) == 1:
                self._num_2D=Vector2D(val[0], val[0])
            elif len(val) > 1:
                self._num_2D=Vector2D(val[0], val[1])
            else:
                self._num_2D=Vector2D(0.0, 0.0)
        elif isinstance(val, Vector2D):
            self._num_2D=val
        else:
            self._num_2D=Vector2D(val)

    @property
    def numeric3D(self):
        return self.c.tuples

    # =================== movement values ==================== #
    def move_normal(self, magnitude):
        self.c += self.normal * magnitude * self.mask()

    def move_angle(self, magnitude, angle = 0.0):
        """Moves a vertex a certain distance along its normal"""
        self.c += self.normal.rotate2D(angle) * magnitude * self.mask()

    def move_hook(self, mag_n, mag_t):
        mv_vec = self.normal * mag_n * self.mask()
        mv_vec += self.tangent * mag_t * self.mask("tangent")
        self.c += mv_vec

    def move_perp(self, mag_n, mag_p):
        mv_vec = self.normal * mag_n * self.mask()
        mv_vec += self.perpendicular * mag_p * self.mask("perpendicular")
        self.c += mv_vec

    def move_triple(self, mag_n, mag_t, mag_p):
        mv_vec = self.normal * mag_n * self.mask()
        mv_vec += self.tangent * mag_t * self.mask("tangent")
        mv_vec += self.perpendicular * mag_p * self.mask("perpendicular")
        self.c += mv_vec

    # =================== duplicate values =================== #
    def create_duplicate(self):
        return 
    def create_perp(self, )

    # ===================== mask values ====================== #
    def mask(self, flag="default"):
        return self._mask[flag].get_val(self)

    def set_mask(self, mask=None, flag="default"):
        if mask is None:
            try:
                self._mask[flag]
            except:
                self._mask[flag]=NoneFunction()
        else:
            self._mask[flag]=mask
            

    # ===================== hash values ====================== #
    def hash(self):
        if self._hash is None:
            print("no hash set")
        return self._hash

    def set_hash(self, dimension=1, spacing=10.0, digit_length=4):
        if dimension==1:
            self._hash=int(self.numeric1D/spacing)
        elif dimension==2:
            self._hash=self.numeric2D.get_hash(spacing, digit_length)
        else:
            self._hash=self.numeric3D.get_hash(spacing, digit_length)

    # ===================== arithmetics ====================== #
    # def add(self, other=None, z_shift=None):
    #     if other is None:
    #         new_loc = Vector3D(self.c)

    #     elif isinstance(other, Vertex):
    #         # print("adding Vertex")
    #         new_loc = self.c + other.c

    #     elif isinstance(other, Vector3D):
    #         # print("adding Vector3D")
    #         new_loc = other + self.c
        
    #     elif isinstance(other, int) or isinstance(other, float):
    #         # print("adding Number")
    #         new_loc = self.c + self.normal * other

    #     if z_shift is None:
    #         pass
    #     else:
    #         new_loc += Vector3D(0,0,z_shift)
        
    #     if Vertex.V_FIELD == "2D":
    #         return Vertex(new_loc, Vector3D(self.normal), self.n_v.add(z_shift) )
    #     else:
    #         return Vertex(new_loc, Vector3D(self.normal) )

    # =================== representations ==================== #
    def return_str(self):
        """Returns the tuple values of this point"""
        str_list=[
            "Vertex object with location: {}, {}, {}".format(self.x, self.y, self.z),
            " and origin: {}, {}, {}".format(self.o.x, self.o.y, self.o.z)
        ]
        if not(self._n is None):
            x,y,z = self._n.tuples
            str_list.append("  with normal: {}, {}, {}".format(x,y,z) )
        if not(self._t is None):
            x,y,z = self._t.tuples
            str_list.append("  with tangent: {}, {}, {}".format(x,y,z) )
        if not(self._p is None):
            x,y,z = self._p.tuples
            str_list.append("  with perpendicular: {}, {}, {}".format(x,y,z) )

        u, v=self.numeric2D
        x, y, z=self.numeric3D
        str_list.extend([
            "  Num 1D: {}".format(self.numeric1D),
            "  Num 2D: {}, {}".format(u,v),
            "  Num 3D: {}, {}, {}".format(x,y,z)
        ])

        return '\n'.join(str_list)

    def __repr__(self):
        return self.return_str()