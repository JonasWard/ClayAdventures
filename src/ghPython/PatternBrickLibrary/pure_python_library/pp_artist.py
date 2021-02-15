import Rhino.Geometry as rg

def createMesh(pp_mesh):
    vs, gs = pp_mesh.rhino_data()
    locMesh = rg.Mesh()
    [locMesh.Vertices.Add(v.tuples) for v in vs]
    [locMesh.Faces.AddFaces(tpl) for tpl in gs]

    return locMesh