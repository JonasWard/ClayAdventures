import Rhino.Geometry as rg

pts_a = []
pts_b = []

for i in range(x + 1):
    for j in range(y + 1):
        pts_a.append(pln.Origin + pln.XAxis * (i - .5 * x) * spacing + pln.YAxis * j * spacing )

for i in range(x + 1):
    for j in range(y + 1):
        pts_b.append(pln.Origin + pln.XAxis * (i - .5 * x) * spacing + pln.YAxis * j * spacing + pln.ZAxis * spacing )

pts = pts_a + pts_b

msh = rg.Mesh()
for pt in pts:
    msh.Vertices.Add(pt)

cnt = len(pts) / 2

for i in range(x):
    id_x_a = i * (y + 1)
    id_x_b = (i + 1) * (y + 1)
    for j in range(y):
        print(id_x_a + j, id_x_a + j + 1, id_x_b + j + 1, id_x_b + j )
        msh.Faces.AddFace(id_x_a + j, id_x_a + j + 1, id_x_b + j + 1, id_x_b + j )
        msh.Faces.AddFace(id_x_b + j + cnt, id_x_b + j + 1 + cnt, id_x_a + j + 1 + cnt, id_x_a + j + cnt )

for i in range(x):
    id_x_a = i * (y + 1)
    id_x_b = (i + 1) * (y + 1)

    msh.Faces.AddFace( id_x_a, id_x_b, cnt + id_x_b, cnt + id_x_a )
    # msh.Faces.AddFace( cnt + id_x_a, cnt + id_x_b, id_x_b, id_x_a )
    # msh.Faces.AddFace( id_x_a + x + 1, id_x_b + x + 1, cnt + id_x_b + x + 1, cnt + id_x_a + x + 1 )
    msh.Faces.AddFace( cnt + id_x_a + y, cnt + id_x_b + y, id_x_b + y, id_x_a + y )
        
for i in range(y):
    # msh.Faces.AddFace( i, i + 1, cnt + i + 1, cnt + i )
    msh.Faces.AddFace( cnt + i, cnt + i + 1, i + 1, i )
    msh.Faces.AddFace( (y + 1) * x + i, (y + 1) * x + i + 1, (y + 1) * x + cnt + i + 1, (y + 1) * x + cnt + i )
    # msh.Faces.AddFace( (y + 1) * x + cnt + i , (y + 1) * x + cnt + i + 1, (y + 1) * x + i + 1, (y + 1) * x + i)
    
values = (x, y)