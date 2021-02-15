class Face:
    def __init__(self, center = None, h_edges = [], connected_faces = [] ):
        self.h_edges = h_edges
        self.center = center
        self.connected_faces = set(connected_faces)

    def link_face(self, n_face):
        self.connected_faces.add(n_face)

    def construct_h_edges(self, distance, max_angle):
        self.