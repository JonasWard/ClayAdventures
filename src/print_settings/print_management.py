class GeometrySettings:

    def __init__(self):

        self.empty = None

    def __repr__(self):

        return self.empty

class GCodeGenerator:

    def __init__(self, geometry, settings = None):

        if not(isinstance(geometry, list)):

            geometry = [geometry]

        for geo in geometry:

            if isinstance(geo, GCodeGenerator):

                print("is gcode object")

                self.settings = geo.settings
            
            else:

                print(type(geo))

                self.settings = settings

settings = GeometrySettings()

geo_0 = GCodeGenerator([], settings)