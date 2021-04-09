# pure python vector class

from math import sin, cos, acos, pi

class Vector2D:
    """Simple vector class for use in 2D (u, v)"""
    TOLERANCE = 0.0001

    def __init__(self, *args):
        """Simple vector class for use in 3D

        Keyword arguments:
        Vector3D    Creates a copy of this instance
        or
        tuple       Initializes a vector with the first two instances
        or
        list        Initializes a vector with the first two instances
        or
        u           float or int coordinate
        v           float or int coordinate
        """

        try:
            if len(args) == 1:
                if isinstance(args[0], Vector3D):
                    self.u, self.v, = args[0].x, args[0].z

                elif isinstance(args[0], Vector3D):
                    self.u, self.v, = args[0].u, args[0].v

                elif isinstance(args[0], tuple) or isinstance(args[0], list):
                    self.__input_numeric_list(args[0])

                elif isinstance(args[0], int) or isinstance(args[0], float):
                    self.x, self.y, self.z = args[0], args[0], args[0]

                else:
                    print("{} is not a valid input type".format(type(args[0])))

            else:
                self.__input_numeric_list(args)
            return True

        except:
            print("invalid input, please either give a list, a tuple, 1 or more float/ints or another Vector3D object")
            return False

    def __input_numeric_list(self, input_list):
        if len(input_list) == 0:
            print("invalid input, please either give a list, a tuple, 1 or more float/ints or another Vector3D object")
        elif len(input_list) == 1:
            self.u, self.v= input_list[0], input_list[0]
        else:
            self.u, self.v = input_list[0], input_list[1]

    @property
    def length(self):
        return (self.u**2 + self.v**2) ** .5

    def __add__(self, other):
        return Vector2D(self.u + other.u, self.v + other.v)

    def add(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return Vector2D(self.u, self.v + other)
        elif isinstance(other, Vector2D):
            return self + other
        elif isinstance(other, Vector3D):
            return Vector2D(self.u + other.z)
        else:
            print("add is not defined for tupe {}".format(type(other)))

    def distance(self, other):
        return (self - other).length

    @property
    def tuples(self):
        return self.u, self.v
    

class Vector3D:
    """Simple vector class for use in 3D (x, y, z)"""
    TOLERANCE = 0.0001

    def __init__(self, *args):
        """Simple vector class for use in 3D

        Keyword arguments:
        Vector3D    Creates a copy of this instance
        or
        tuple       Initializes a vector with the first three instances
        or
        list        Initializes a vector with the first three instances
        or
        x           float or int coordinate
        y           float or int coordinate
        z           float or int coordinate
        """

        try:
            if len(args) == 1:
                if isinstance(args[0], Vector3D):
                    self.x, self.y, self.z = args[0].x, args[0].y, args[0].z

                elif isinstance(args[0], tuple) or isinstance(args[0], list):
                    self.__input_numeric_list(args[0])

                elif isinstance(args[0], int) or isinstance(args[0], float):
                    self.x, self.y, self.z = args[0], args[0], args[0]

                else:
                    print("{} is not a valid input type".format(type(args[0])))

            else:
                self.__input_numeric_list(args)

        except:
            print("invalid input, please either give a list, a tuple, 1 or more float/ints or another Vector3D object")

    def __input_numeric_list(self, input_list):
        if len(input_list) == 0:
            print("invalid input, please either give a list, a tuple, 1 or more float/ints or another Vector3D object")
        elif len(input_list) == 1:
            self.x, self.y, self.z = input_list[0], input_list[0], input_list[0]
        elif len(input_list) == 2:
            self.x, self.y, self.z = input_list[0], input_list[1], 0.0
        else:
            self.x, self.y, self.z = input_list[0], input_list[1], input_list[2]

    def __add__(self, other):
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mod__(self, other):
        return self.x * other.y - self.y * other.x

    def __mul__(self, other):
        if isinstance(other, Vector3D):
            return self.x * other.x + self.y * other.y
        
        elif isinstance(other, int) or isinstance(other, float):
            return Vector3D(
                self.x * other,
                self.y * other,
                self.z * other
            )

        else:

            return Vector3D(self.x * other, self.y * other)

    def __iter__(self):
        for i in range(3):
            yield self[i]

    def __getitem__(self, idx):
        if idx == 0:
            return self.x

        elif idx == 1:
            return self.y

        elif idx == 2:
            return self.z

        else:
            return None

    def normal2D(self):
        """Returns a 90deg turned version of the vector

        Returns:
        normal      Vector3D
        """

        return Vector3D(-self.y, self.x, self.z)

    def __repr__(self):

        return "Vector3D with coordinates: {}, {}, {}".format(self.x, self.y, self.z)

    def __eq__(self, other):

        return self.distance(other) < Vector3D.TOLERANCE

    def distance(self, other):

        return (self - other).length

    @ property
    def length(self):

        return (self.x ** 2.0 + self.y ** 2.0 ) ** .5

    def unitize(self):
        """Sets the length of the vector to 1.0"""

        l = self.length if self.length > Vector3D.TOLERANCE else 1.0

        self.x /= l
        self.y /= l
        self.z /= l

    def rotate2D(self, other):

        x, y = self.x, self.y
        if isinstance(other, Vector3D):
            other = other.unit_copy(True)
            c, s = other.x, other.y

        elif other == 0.0:
            return self

        else:
            c, s = cos(other), sin(other)

        #2D transformation
        return Vector3D(c * x + s * y, - s * x + c * y, self.z)

    def unit_copy(self, dimension_2 = False):
        """Returns a unitized copy of the vector"""

        if dimension_2:
            vec = Vector3D(self.x, self.y)
            vec.unitize()
            return Vector3D(vec.x, vec.y, self.z)

        else:
            vec = Vector3D(self)
            vec.unitize()
            return vec

    @property
    def angle2D(self):
        """Calculates the positive angle the vector makes with the x-axis

        Returns:
        Angle       Float
        """

        if self.length < Vector3D.TOLERANCE:
            alfa = 0.0

        else:
            vec = self.unit_copy(True)
            quadrant_angle = acos( abs(vec.x) )

            if vec.x > 0.0 and vec.y > 0.0:
                alfa = quadrant_angle
            
            elif vec.y < 0.0 and vec.x < 0.0:
                alfa = pi + quadrant_angle

            elif vec.y > 0.0:
                alfa = pi - quadrant_angle

            else:
                alfa = 2 * pi - quadrant_angle

        return alfa

    # def return_tuple(self):
    #     """Returns a tuple of this vector"""

    #     return (self.x, self.y, self.z)

    @property
    def tuples(self):
        return self.x, self.y, self.z

    def angle_vec(self, other):
        """Calculates the angle of the triangel defined by this and 2 more points

        Keyword arguments:
        v_a         Previous vector

        Returns:
        angle       float
        """
        cos_val = self * other / (self.length * other.length)

        if cos_val > .999999:
            return 0.0
        elif cos_val < -.999999:
            return pi
        else:
            return acos(cos_val)