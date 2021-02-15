import Rhino.Geometry as rg
import vertexClass_v1 as vc

class MeshObject:
    TRI = True

    def __init__(self, plane, width, height, spacing):
        self.pln = plane
        self.w = width
        self.h = height
        self.s = spacing

        self.x = int(width / spacing)
        self.y = int(height / spacing)

        self.front_pts = []
        self._front_init = False
        self.back_pts = []

    def construct_pts(self):
        b_pt = self.pln.Origin
        x_a = self.pln.XAxis
        y_a = self.pln.YAxis
        z_a = self.pln.ZAxis

        for i in range(self.x + 1):
            for j in range(self.y + 1):
                self.front_pts.append(b_pt + x_a * (i - .5 * self.x) * self.s + y_a * j * self.s )

        for i in range(self.x + 1):
            for j in range(self.y + 1):
                self.back_pts.append(b_pt + x_a * (i - .5 * self.x) * self.s + y_a * j * self.s + z_a * self.s )


    def add_front_pts(self, pts, inverse = False):
        if inverse:
            self.front_pts = self._invert_points(pts)
        else:
            self.front_pts = pts
        
        self._front_init = True

    def adjusting_front_pts(self):
        # adjusting the front points based on their distance to the base plane
        if self._front_init:

            distances = []
            b_pts = []

            for pt in self.front_pts:
                c_pt = self.pln.ClosestPoint(pt)
                b_pts.append(c_pt)
                distances.append(rg.Vector3d.Multiply(rg.Vector3d(pt - c_pt),self.pln.ZAxis))
            
            self.front_pts = []
            min_val = min(distances)
            print(min_val)
            for i, b_pt in enumerate(b_pts):
                self.front_pts.append(b_pt + (distances[i] - min_val) * self.pln.ZAxis)
        else:
            print("Front has not been set")

    def construct_layers(self):
        layer_set = []
        m = self.x + 1
        n = self.y + 1

        for i in range(self.y + 1):
            y_val = i * self.s

            local_layer = []

            for j in range(self.x + 1):
                x_val = j * self.s
                    
                loc_pt = self.front_pts[i + j * n]
                
                loc_vertex = vc.Vertex(loc_pt, -self.pln.ZAxis, x_val, y_val)
                
                local_layer.append(loc_vertex)
            layer_set.append(local_layer)
                
        return layer_set

    def _invert_points(self, pt_list):
        m = self.x + 1

        inverse_pt_list = [[] for i in range(m)]

        for idx, pt in enumerate(pt_list):
            m_val = idx % m
            n_val = int ( (idx - m_val) / m )
            
            inverse_pt_list[m_val].append(pt)
            
        n_pt_list = []

        for pt_set in inverse_pt_list:
            n_pt_list.extend(pt_set)
            
        return n_pt_list

    def construct_graph(self):
        cnt = len(self.back_pts)

        face_list = []

        if MeshObject.TRI:
            for i in range(self.x):
                id_x_a = i * (self.y + 1)
                id_x_b = (i + 1) * (self.y + 1)
                for j in range(self.y):
                    print(id_x_a + j, id_x_a + j + 1, id_x_b + j + 1, id_x_b + j )
                    face_list.append([id_x_a + j, id_x_a + j + 1, id_x_b + j + 1])
                    face_list.append([id_x_a + j, id_x_b + j + 1, id_x_b + j])
                    face_list.append([id_x_b + j + cnt, id_x_b + j + 1 + cnt, id_x_a + j + 1 + cnt, id_x_a + j + cnt])

        else:
            for i in range(self.x):
                id_x_a = i * (self.y + 1)
                id_x_b = (i + 1) * (self.y + 1)
                for j in range(self.y):
                    print(id_x_a + j, id_x_a + j + 1, id_x_b + j + 1, id_x_b + j )
                    face_list.append([id_x_a + j, id_x_a + j + 1, id_x_b + j + 1, id_x_b + j])
                    face_list.append([id_x_b + j + cnt, id_x_b + j + 1 + cnt, id_x_a + j + 1 + cnt, id_x_a + j + cnt])

        for i in range(self.x):
            id_x_a = i * (self.y + 1)
            id_x_b = (i + 1) * (self.y + 1)

            face_list.append([id_x_a, id_x_b, cnt + id_x_b, cnt + id_x_a])
            face_list.append([cnt + id_x_a + self.y, cnt + id_x_b + self.y, id_x_b + self.y, id_x_a + self.y])
                
        for i in range(self.y):
            face_list.append([cnt + i, cnt + i + 1, i + 1, i])
            face_list.append([(self.y + 1) * self.x + i, (self.y + 1) * self.x + i + 1, (self.y + 1) * self.x + cnt + i + 1, (self.y + 1) * self.x + cnt + i])

        return face_list

    def construct_mesh(self):
        msh = rg.Mesh()
        if self._front_init:
            # initializing the points
            for pt in self.front_pts + self.back_pts:
                msh.Vertices.Add(pt)

            for f in self.construct_graph():
                if len(f) == 4:
                    msh.Faces.AddFace(f[0], f[1], f[2], f[3])
                elif len(f) == 3:
                    msh.Faces.AddFace(f[0], f[1], f[2])

            return msh
        else:
            print("Front has not been set")
            return msh