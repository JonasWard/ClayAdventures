# defining a class you can pass on that runs then a certain function

class Pattern(object):

    def __init__(self, a, b):

        self.a = a
        self.b = b

    def operateOn(self, vertex):

        vertex.x += self.a
        vertex.y += self.b

class Vertex(object):

    def __init__(self, x, y):

        self.x = x
        self.y = y

    def __repr__(self):

        str_set = [
            'this this is a vertex with x value:',
            str(self.x),
            'and y value:',
            str(self.y),
        ]

        return ' '.join(str_set)

    def applyPattern(self, pattern):

        pattern.operateOn(self)

ver = Vertex(1, 2)

pat = Pattern(.1, .2)

print(ver)

ver.applyPattern(pat)

print(ver)