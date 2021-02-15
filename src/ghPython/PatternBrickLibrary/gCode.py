# g code generator for clay extrusions

def gCodeLine(generation):

    def __init__(self, coordinates, z_val = True, extrusion_value = None, feed_value = None, absolute_relative = None):

        self.X = coordinates.X
        self.Y = coordinates.Y

        if z_val:

            self.Z = coordinates.Z
        
class GCodeSettings:

    def __init__(self):

        self.nozzle_bool = False
        self.feed_rate_bool = False
        self.extrusion_rate_bool = False
        self.layers_bool = False
        self.geometry_bool = False
        self.distance_bool = False
        self.diamond_bool = False

    def setNozzle(self, diameter):

        self.nozzle_bool = True
        self.nozzle_settings = ['diameter: ', str(diameter)]

    def setFeedRate(self, standard, max_body = None, min_pin = None, max_pin = None):

        self.feed_rate_bool = True
        self.feed_rate_settings = ['base feed rate:', str(standard)]

        if not(max_body == None):

            se

# class GCodeGenerator(object):

#     def __init__(self, paths, relative = False):

#         self.paths = paths
#         self.relative = relative

#         self.extrusion_rate = .3    # per mm
#         self.z_offset = 1.1         # in mm

#     def distanceCalculation(self, set): 

#     def startStopRoutine(self, lift_height, extrusion_decrese, wait_times):


#     def gCodeStringGeneration(self):

