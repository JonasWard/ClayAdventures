import Rhino.Geometry as rg

def offsetCrv(crv, distance, direction):

    if direction == "inside":

        direction = -1

    elif direction == "outside":

        direction = 1

    pln = rg.Plane(crv.PointAt(0.0), rg.Vector3d(0,0,1))

    tmp_offset_crv_1 = crv.Offset(pln, 1.0, .01, rg.CurveOffsetCornerStyle.Round)[0]
    tmp_offset_crv_2 = crv.Offset(pln, -1.0, .01, rg.CurveOffsetCornerStyle.Round)[0]

    if tmp_offset_crv_1.GetLength() < tmp_offset_crv_2.GetLength():

        crv.Reverse()
    
    else:

        direction *= 1