import Rhino.Geometry as rg

class OffsetType(object):

    def __init__(self, count = 2, direction = "outside", distance = 1.1, boundary = 1.0):
        
        # # key values:
        # self.cnt = 0.0
        # self.dis = 0.0
        # self.bou_dis = 0.0
        # self.dis_set = []

        self.cnt_min = 1
        self.cnt_max = 10

        self.dis_min = 0.5
        self.dis_max = 20.0

        self.bou_min = .2
        self.bou_max = 1.5

        self.setCount(count)
        self.setDistance(distance)
        self.setDirection(direction)
        self.setBoundaryValue(boundary)

        self.generateDisSet()

    def generateDisSet(self, count = None, distance = None, direction = None, boundary = None):

        if not(count == None):

            self.setCount(count)

        if not(distance == None):

            self.setDistance(distance)

        if not(direction == None):

            self.setDistance(direction)

        if not(boundary == None):

            self.setBoundaryValue(boundary)

        self.dis_set = [(self.start + i) * self.dis for i in range(self.cnt)]

    def setCount(self, count):

        self.cnt = int(count)

        if self.cnt < self.cnt_min:
            self.cnt = self.cnt_min

        elif self.cnt > self.cnt_max:
            self.cnt = self.cnt_max

    def setDistance(self, dis):

        self.dis = abs(float(dis))

        if self.dis < self.dis_min:
            self.dis = self.dis_min

        elif self.dis > self.dis_max:
            self.dis = self.dis_max

    def setDirection(self, direction):

        # default: direction == "outside"
        self.start = 0.0

        if direction == "inside":

            self.start = (1 - self.cnt)

        elif direction == "middle":
            
            self.start = (1 - self.cnt) * .5

    def setBoundaryValue(self, boundary):

        self.bou_dis = abs(float(boundary))
        
        bou_min = self.bou_min * self.dis
        bou_max = self.bou_max * self.dis

        if self.bou_dis < bou_min:

            self.bou_dis = bou_min

        elif self.bou_dis > bou_max:

            self.bou_dis = bou_max


class LinkType(object):

    def __init__(self, split_object = None, split_length = 3.0, link_logic = "intersect", open_side = "inside"):

        self.dis = 0.0


    def splitFunction(self):

    def __splitLines(self, lines):

    def __splitPoints(self, points):

        # in case there is only one 
        

class CurveSet(object):

    def __init__(self, curve, offset_type, merge_type):

        pass
