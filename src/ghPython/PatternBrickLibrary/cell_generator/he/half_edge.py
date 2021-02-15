class HalfEdge:
    def __init__(self, prev_e = None, next_e = None, pair_e = None, face_f = None, prev_v = None, next_v = None):
        self.prev_e = prev_e
        self.next_e = next_e
        self.pair_e = pair_e
        self.face_f = face_f
        self.prev_v = prev_v
        self.next_v = next_v