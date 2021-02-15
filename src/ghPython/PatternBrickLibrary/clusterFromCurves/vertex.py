import Rhino.Geometry as rg
import math

def signed_vector_angle(a, b):
    return math.atan2( a.X*b.Y - a.Y*b.X, a.X*b.X + a.Y*b.Y )

def positive_vector_angle(a, b):
    angle = signed_vector_angle(a, b)
    if angle > 0:
        return angle
    else:
        return 6.2831853072 + angle

class Vertex:
    MAX_A = 1.8
    DIS = 4.0
    def __init__(self, location):
        self.location = rg.Point3d(location)
        self.neighbours = []
        self.vectors = []
        self.n_locations = []

    @property
    def count(self):
        return len(self.neighbours)

    def add_neighbour(self, other_vertex):
        self.neighbours.append(other_vertex)

    def sort_neighbours(self):
        angles = [n.angle(self) for n in self.neighbours]

        print(angles)
        print(self.neighbours)

        angles, self.neighbours = list(zip(*sorted(zip(angles, self.neighbours) ) ) )
        
        print(angles)
        print(self.neighbours)

    def angle(self, other):
        n_vec = rg.Vector3d(self.location - other.location)
        return positive_vector_angle(rg.Vector3d.XAxis, n_vec)

    def construct_dir_vectors(self):

        if self.count == 0:
            b_vec = rg.Vector3d(Vertex.DIS, 0, 0)
            
            self.interpolate_vectors_end(b_vec)

        elif self.count == 1:
            b_vec = rg.Vector3d(self.neighbours[0].location - self.location)
            self.vectors.append(b_vec * .5)

            self.interpolate_vectors_end(b_vec)

        else:
            for i in range(self.count):
                v_0 = rg.Vector3d(.5 * (self.neighbours[i].location - self.location) )
                v_1 = rg.Vector3d(.5 * (self.neighbours[(i + 1) % self.count].location - self.location) )

                self.interpolate_vectors(v_0, v_1)

        print("vector count : {}".format(len(self.vectors)))

    def interpolate_vectors(self, v_0, v_1):
        # initialize the first vectors of the two as a normal vector
        self.vectors.append(rg.Vector3d(v_0) )
        
        # getting the positive angle
        angle = positive_vector_angle(v_0, v_1)

        print(angle)

        if angle > Vertex.MAX_A:

            angle_count = math.ceil( angle / Vertex.MAX_A )
            angle_delta = angle / angle_count

            print("angle count : {}".format(angle_count) )

            b_vec = rg.Vector3d(v_0)
            b_vec.Unitize()
            b_vec = b_vec * Vertex.DIS

            for i in range(1, int(angle_count), 1):
                r_matrix = rg.Transform.Rotation(i * angle_delta, self.location)
                n_vec = rg.Vector3d(b_vec)
                n_vec.Transform(r_matrix)
                self.vectors.append(n_vec)
                print("added a vector")

    def interpolate_vectors_end(self, b_vec):
        angle_count = math.ceil( math.pi * 2.0 / Vertex.MAX_A )
        angle_delta = math.pi * 2.0 / angle_count

        loc_v = rg.Vector3d(b_vec)
        loc_v.Unitize()
        loc_v = loc_v * Vertex.DIS

        for i in range(1, int(angle_count), 1):
            r_matrix = rg.Transform.Rotation(i * angle_delta, self.location)
            n_vec = rg.Vector3d(loc_v)
            n_vec.Transform(r_matrix)
            self.vectors.append(n_vec)

    def new_location(self):
        for i in range(len(self.vectors) ):
            self.n_locations.append(rg.Point3d(self.location + self.vectors[i] + self.vectors[(i + 1) % len(self.vectors) ]) )

    def curve_representation(self):
        return rg.Polyline(self.n_locations + [self.n_locations[0]] ).ToNurbsCurve()

    def line_representation(self):
        return [rg.Line(self.location, n_l) for n_l in self.n_locations]