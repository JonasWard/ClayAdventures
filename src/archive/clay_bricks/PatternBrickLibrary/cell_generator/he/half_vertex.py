import Rhino.Geometry as rg

class Vertex:
    def __init__(self, location = [] ):
        self._location = location

    @location.getter
    def location(self):
        if isinstance(self._location, list) :
            t_pt = rg.Point3d(0,0,0)
            for pt in self._location:
                t_pt = t_pt + pt

            return t_pt * (1.0 / len(self.location) )
        else :
            return self._location

    @location.setter
    def location(self, new_val):
        self._location = new_val

    def addLocationVal(self, extra_val):
        if not(isinstance(self._location, list) ) :
            t_pt = rg.Point3d(self._location)
            self._location = [t_pt]

        self.addLocationVal(extra_val)


    def _addLocationval(self, extra_val):
        if isinstance(extra_val, list):
            self._location.extend(extra_val)
        else:
            self._location.append(extra_val)