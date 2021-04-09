from pp_distance_functions import NoneFunction

class Mesh():
    def rhino_data(self):
        return self.vs, self.gs

    def add_sdf(self, sdf):
        self.sdf=True
        self.sdf=sdf

    def add_mask(self, sdf, flag="default"):
        [v.add_mask(sdf) for v in self.vs]

    def apply(self, move_type="normal"):
        print("applying mesh")
        for v in self.vs:
            mv_val=self.sdf.get_val(v)
            v.move_normal(mv_val)

class BaseMesh(Mesh):
    def __init__(self, vertex_list, connection_graph):
        self.vs = vertex_list
        self.gs = connection_graph

        self.sdf=False

class StackedMesh(Mesh):
    MAX_PT_COUNT=15000

    def __init__(self, base_vs, layer_height, layer_count):
        self.sdf=False

        self.vs=[]
        self.gs=[]

        self.l_h = layer_height
        self.l_c = layer_count

        self.b_vs=base_vs

    def construct_mesh(self, h_sdf=NoneFunction() ):
        pt_count = int(len(self.b_vs) / 2)

        layer_count+=0

        while layer_count < self.l_c:
            for i in range(-layer_count % 2, len(self.b_vs), 2):
                x, y, z = pts[i].X, pts[i].Y, current_h
                pt_list.append(rg.Point3d(x, y, z) )
                p_list.append(rg.Vector3d(tangents[i]) )
                mesh_obj.Vertices.Add(x, y, z)
            
            if layer_count > 0:
                base_count = (layer_count - 1) * pt_count
                b_idx = base_count
                s_idx = base_count + pt_count
                
                if layer_count%2 == 1:
                    for i in range(pt_count):
                        i_2 = (i + 1) % pt_count
                        g_list.append( (b_idx + i, b_idx + i_2, s_idx + i_2) )
                        g_list.append( (b_idx + i, s_idx + i_2, s_idx + i) )
                        
                else:
                    for i in range(pt_count):
                        i_2 = (i + 1) % pt_count
                        g_list.append( (b_idx + i, b_idx + i_2, s_idx + i) )
                        g_list.append( (b_idx + i_2, s_idx + i_2, s_idx + i) )
                        
            current_h += l_height
            layer_count += 1