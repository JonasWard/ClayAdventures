import Rhino.Geometry as rg
import math

class CellBase:
    def __init__(self, location, neighbours = []):
        self.location = location
        self.neighbours = neighbours

    def neighbour_count(self):
        return len(self.neighbours)

    def get_angles(self):
        if self.neighbour_count > 1:
            vs = []

            for ng in self.neighbours:
                v = rg.Vector3d(ng.location - self.location)
                v.Unitize()
                vs.append( v )

            angle_list = []

            for i in range(self.neighbour_count - 1):

                x0, x1 = v0.X, v1.X
                y0, y1 = v0.Y, v1.Y
                
                angle = math.atan2(x0*y1-y0*x1,x0*x1+y0*y1)

                if angle < 0.0:
                    angle = math.pi * 2.0 + angle
                
                angle_list.append(angle)

        elif self.neighbour_count == 1:
            return [math.pi * 2.0]

        else:
            return 0

        
        
