class Vector():

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    @property
    def tuples(self):
        return self.x, self.y, self.z

if __name__=="__main__":
    v=Vector(0., 1., 2)
    print(v.tuples)
    x,y,z=v.tuples
    print(x, y, z)