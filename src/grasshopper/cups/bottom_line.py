import Rhino.Geometry as rg

# # the grasshopper input variables:
# base_crvs # the curves which make out the bottom of the cup
# body_crvs # the curves that make out the rest of the cup
# layer_height   # float
# bottom_spacing # the amount the bottom curves get offseted
# changing_height # bool
# changing_height_range # tuple
# changing_height_periods # float

# # detetcting the outer points of the curves

# getting the center point

def create_geometry(base_crvs, body_crvs, layer_height, bottom_height, changing_height, changing_height_range, changing_height, periods)

    pt_0_0, pt_0_1 = base_crvs[0].PointAtEnd, base_crvs[0].PointAtStart
    pt_1_0, pt_1_1 = base_crvs[1].PointAtEnd, base_crvs[1].PointAtStart

    if pt_0_0.DistanceTo(pt_1_0) < .1 or pt_0_0.DistanceTo(pt_1_1) < .1:

        c_pt = pt_0_0

    else:

        c_pt = pt_0_1

    # offseting curves

    b_plane = rg.Plane.WorldXY
    c_style = rg.CurveOffsetCornerStyle.Round

    for b_crv in base_crvs:

        a = b_crv.Offset(b_plane, .5 * bottom_spacing, .01, c_style)
        b = b_crv.Offset(b_plane, - .5 * bottom_spacing, .01, c_style)

        a_line = rg.Line(
            a.PointAtEnd,
            b.PointAtEnd
        ).ToNurbseCurve()

        b_line = rg.Line(
            a.PointAtStart,
            b.PointAtStart
        ).ToNurbseCurve()