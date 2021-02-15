from Rhino.Geometry import Point3d, Line, Arc, PolyCurve
from standard_settings import default_production_dict, default_brick_geometry_dict

class StandardObject:
    """class that allows you to initialize the parameters of a simple brick"""
    def __init__(self, parameters=None, production_parameters=None):
        if parameters is None:
            parameters=default_brick_geometry_dict

        if production_parameters is None:
            production_parameters=default_production_dict

        lw=[parameters["brick_length"],parameters["brick_width"]]
        self.l=min(lw)
        self.w=max(lw)
        self.l_half=self.l*.5
        self.w_half=self.w*.5
        self.s_pin=parameters["pin_spacing"]
        
        self.h_pin=parameters["height_pin"]
        self.h_body=parameters["height_body"]
        
        self.h_start=parameters["start_height"]
        self.h_layer=production_parameters["layer_height"]

        self._calculate_heights()

    def _calculate_heights(self):
        self.hs_body=[]
        self.hs_pin=[]

        h=self.h_start

        while h < self.h_body:
            self.hs_body.append(h)
            h+=self.h_layer
            
        while h < self.h_pin:
            self.hs_pin.append(h)
            h+=self.h_layer

    def pin_heights(self):
        return self.hs_pin

    def body_heights(self):
        return self.hs_body

    def pin_points(self):
        return [
            Point3d(-.5*self.s_pin, 0, 0),
            Point3d(.5*self.s_pin, 0, 0)
        ]

    def base_profile(self):
        #     *       *
        #   *            *
        #     *       *

        # static variable lists
        val_list = [(1,1), (1, -1), (-1, -1), (-1, 1)]

        # generating the points
        pts = []
        for i in range(4):
            pts.append(Point3d(
                self.l_half*val_list[i][0],
                self.w_half*val_list[i][1],
                0.0
            ))
            
            if i==0:
                pts.append(Point3d(self.l_half+self.w_half, 0, 0))
                
            elif i == 2:
                pts.append(Point3d(-(self.l_half+self.w_half), 0, 0))

        # creating the segments
        poly_crv=PolyCurve()
        for i in range(2):
            p0, p1, p2, p3 = [pts[j+i*3] for j in range(-1, 3, 1)]
            
            line = Line(p0, p1)
            poly_crv.Append(line)
            
            crv = Arc(p1, p2, p3)
            poly_crv.Append(crv)

        return poly_crv