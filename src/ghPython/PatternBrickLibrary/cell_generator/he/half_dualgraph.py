import half_face

def from_dual_graph(locations = [], links = []):
    faces = []
    for location in locations:
        faces.add( Face(location) )

    for link in links:
        faces[ link[0] ].link_face(faces[ link[1] ] )
