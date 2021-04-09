import Rhino.Geometry as rg

class Vertex:
    
    def __init__(self, pt, normal = None):
        
        self.loc = pt
        self.o = pt
        
        if normal == None:
            
            self.n = rg.Point3d(1,0,0)

        else:

            self.n = normal
            
        self.special = False
            
    def offset(self, val):
        
        self.loc += self.n * val
    
    @property
    def X(self):
        
        return self.loc.X
        
    @property
    def Y(self):
        
        return self.loc.Y
        
    @property
    def Z(self):
        
        return self.loc.Z
        
    def addVertex(self, other):
        
        self.loc += other.loc
        self.n = (self.n + other.n) * .5
        
    def addPoint(self, other):
        
        self.loc += other

    def add(self, other):
        if isinstance(other, Vertex):
            # print("adding Vertex")
            new_loc = self.loc + other.loc

        elif isinstance(other, rg.Point3d):
            # print("adding Point3d")
            new_loc = other + self.loc
        
        elif isinstance(other, int) or isinstance(other, float):
            # print("adding Number")
            new_loc = self.loc + self.n * other
        
        return Vertex(new_loc, self.n)

    def __add__(self, other):
        return self.add(other)

    def numeric_distance(self, other, radius = 0.0):

        # return ((self.x_val - other.x_val) ** 2 + (self.y_val - other.y_val) ** 2) ** .5

        return self.vec_version.DistanceTo(other.vec_version)


    def x_distance(self, other):

        return abs(self.x_val - other.x_val)


    def move_pt(self, mv_pt):

        return Vertex(self.o + mv_pt, self.n, self.x_val, self.y_val)
        

    def warp_pt(self, scale_val = 0):

        self.v = rg.Point3d(self.o + self.n * (scale_val * self.n_scale))

    def distance_function(self, x_spacing = 20.0, y_spacing = 20.0, layer_shift = 2.0, rot_alfa = 0.0, x_scale_val = 1.0):
        
        x, y = self.x_val, self.y_val

        if not(rot_alfa == 0.0):
            
            x_new = math.cos(rot_alfa) * x - math.sin(rot_alfa) * y
            y_new = math.sin(rot_alfa) * x + math.cos(rot_alfa) * y
            
            x, y = x_new, y_new
        
        layer_shift = float(layer_shift)
        
        abs_loc_y = y % y_spacing
        layer_count = float(math.floor((y - abs_loc_y) / y_spacing))
        
        # print("layer_count %s" % layer_count)
        # print("layer_shift %s" % layer_shift)
        
        x_shift = (layer_count / layer_shift) * x_spacing
        
        # print("x_shift %s" % x_shift)
        
        loc_x = ((x + x_shift) % x_spacing) / x_spacing
        loc_y = abs_loc_y / y_spacing
        
        distance = math.sqrt((loc_x - .5) ** 2 + (loc_y - .5) ** 2)
        
        return distance

class StructuredPolyline:
    
    def __init__(self, pts, closed = True):

        if not(any(pts) ):
            print("you have given me an empty point list")
        elif isinstance(pts[0], rg.Point3d):
            # print("have been given points")
            self.ini_pt_set = pts
            self._makeVertexSet()
        elif isinstance(pts[0], Vertex):
            # print("have been given vetexes")
            self.v_set = pts
        
        self.c = closed
        
    def _makeVertexSet(self):

        self.v_set = None
        tmp_v_set = []
        
        for i in range(self.count):

            tmp_v_set.append(Vertex(
                pt = self.pts(i),
                normal = self.getNormal(i)
            ))

        self.v_set = tmp_v_set

    def add_copy(self, mv_vs=None, z_shift=0.0):
        mv_pt = rg.Point3d(0,0,z_shift)
        loc_vs = [v.add(mv_pt) for v in self.v_set]
        if not(mv_vs == None):
            loc_vs = [v.add(mv_vs[i%len(mv_vs)]) for i, v in enumerate(loc_vs)]

        return StructuredPolyline(loc_vs)
            
    def indexNorm(self, index):
        
        return index % self.count

    def pts(self, index):
        
        i = self.indexNorm(index)
        
        if self.v_set == None:
            
            return self.ini_pt_set[i]
        
        else:
            
            return self.v_set[i].loc

    def pointSet(self):

        return [v.loc for v in self.v_set]

    def interpolatedPoint(self, index):

        i = int(index)
        t_val = index - i

        j = i + 1

        pt_0 = self.pts(i)
        pt_1 = self.pts(j)

        new_vertex = Vertex(
            pt_0 + (pt_1 - pt_0) * t_val,
            self.getNormal(index)
        )

        return new_vertex

    def addPoint(self, index):

        v_set_a = self.v_set[:]

    @property
    def count(self):
        
        if self.v_set == None:
            
            return len(self.ini_pt_set)
        
        else:
            
            return len(self.v_set)
            
    def getDir(self, index):
        
        i = self.indexNorm(index)
        
        if i == self.count - 1:
            
            dir_vec = self.pts(-1) - self.pts(-2)

        else:

            dir_vec = self.pts(i + 1) - self.pts(i)
            
        size = (dir_vec.X ** 2 + dir_vec.Y ** 2) ** .5
            
        return dir_vec / size
    
    def getNormal(self, index):
        
        i = self.indexNorm(index)

        if (int(i) == i):
            # case you get a corner point
        
            if i == 0 or i == self.count - 1:
                
                dir_vec = self.getDir(i)
                
            else:

                dir_vec_a = self.getDir(i - 1)
                dir_vec_b = self.getDir(i)
                
                dir_vec = (dir_vec_a + dir_vec_b) * .5

        else:
            # case you get point on a line segment

            dir_vec = self.getDir(int(i))

        normal = rg.Point3d(
            dir_vec.Y,
            -dir_vec.X,
            0
        )

        return normal

    def offset(self, distance):

        if self.v_set == None:

            self._makeVertexSet()

        for v in self.v_set:

            v.offset(distance)

    def toPolyline(self):

        pt_set = []

        for i in range(self.count):

            pt_set.append(self.pts(i))

        if self.c:

            pt_set += [pt_set[0]]

        return rg.Polyline(pt_set).ToPolylineCurve()


            
    
    