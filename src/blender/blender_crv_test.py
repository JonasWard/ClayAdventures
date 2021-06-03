import bpy
from mathutils import Vector

coords_list = [[0,1,2], [1,2,3], [-3,2,1], [0,0,-4]]

# make a new curve
crv = bpy.data.curves.new('crv', 'CURVE')
crv.dimensions = '3D'

# make a new spline in that curve
spline = crv.splines.new(type='NURBS')

# a spline point for each point
spline.points.add(len(coords_list)-1) # theres already one point by default

# assign the point coordinates to the spline points
for p, new_co in zip(spline.points, coords_list):
    p.co = (new_co + [1.0]) # (add nurbs weight)

# make a new object with the curve
obj = bpy.data.objects.new('object_name', crv)
bpy.context.scene.collection.objects.link(obj)