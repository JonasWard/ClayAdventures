from bpy import ops, data, types, context
from math import sin, cos

HILBERT_MAP = {
    'S': ['W', 'S', 'S', 'E'],
    'W': ['S', 'W', 'W', 'N'],
    'E': ['N', 'E', 'E', 'S'],
    'N': ['E', 'N', 'N', 'W']
}

POINT_ORDER_MAP = {
    'S': [(-1.0, -1.0), (-1.0, 0.0), (0.0, 0.0), (0.0, -1.0)],
    'W': [(-1.0, -1.0), (0.0, -1.0), (0.0, 0.0), (-1.0, 0.0)],
    'E': [(0.0, 0.0), (-1.0, 0.0), (-1.0, -1.0), (0.0, -1.0)],
    'N': [(0.0, 0.0), (0.0, -1.0), (-1.0, -1.0), (-1.0, 0.0)]
}


START_LEAVES = {
    "simple" : [
        [(-1., -1., 0.), 'S', .5]
    ],
    "2:1" : [
        [(-1.5,-1,0), 'S', .5],
        [(-.5, -1, 0.), 'S', .5]
    ],
    "square" : [
        [(-1.5,-1.5,0), 'W', .5],
        [(-1.5,-.5,0), 'S', .5],
        [(-.5, -.5, 0.), 'S', .5],
        [(-.5, -1.5, 0.), 'E', .5]
    ],
    "2:3" : [
        [(-1.5,-1.,0), 'W', .5],
        [(-1.5,-0.,0), 'S', .5],
        [(-.5, -0., 0.), 'S', .5],
        [(-.5, -1., 0.), 'E', .5],
        [(-.5, -2., 0.), 'N', .5],
        [(-1.5,-2.,0), 'N', .5]
    ],
    "3:2" : [
        [(-1., .5,0), 'S', .5],
        [(0., .5,0), 'S', .5],
        [(1., .5, 0.), 'S', .5],
        [(1., -.5, 0.), 'N', .5],
        [(0., -.5, 0.), 'N', .5],
        [(-1., -.5,0), 'N', .5]
    ],
    "4:3" : [
        [(-1.5, 0.0, 0), 'W', 0.5],
        [(-1.5, 1.0, 0), 'S', 0.5],
        [(-0.5, 1.0, 0), 'S', 0.5],
        [(-0.5, 0.0, 0), 'E', 0.5],
        [(0.5, 0.0, 0), 'W', 0.5],
        [(0.5, 1.0, 0), 'S', 0.5],
        [(1.5, 1.0, 0), 'S', 0.5],
        [(1.5, 0.0, 0), 'E', 0.5],
        [(1.5, -1.0, 0), 'N', 0.5],
        [(0.5, -1.0, 0), 'N', 0.5],
        [(-0.5, -1.0, 0), 'N', 0.5],
        [(-1.5, -1.0, 0), 'N', 0.5]
    ]
}


def v_add(tpl_a : tuple, tpl_b : tuple) -> tuple:
    return (
        tpl_a[0] + tpl_b[0],
        tpl_a[1] + tpl_b[1],
        tpl_a[2] + tpl_b[2]
    )


def v_sub(tpl_a : tuple, tpl_b : tuple) -> tuple:
    return (
        tpl_a[0] - tpl_b[0],
        tpl_a[1] - tpl_b[1],
        tpl_a[2] - tpl_b[2]
    )


def v_scale(tpl_a : tuple, value : tuple) -> tuple:
    return (
        tpl_a[0] * value,
        tpl_a[1] * value,
        tpl_a[2] * value
    )


def v_len(tpl_a : tuple) -> float:
    return (tpl_a[0] ** 2 + tpl_a[1] ** 2 + tpl_a[2] ** 2) ** .5


def v_distance(tpl_a : tuple, tpl_b : tuple) -> tuple:
    return v_len(v_sub(tpl_a, tpl_b))


def v_sin(tpl: tuple) -> tuple:
    return sin(tpl[0]), sin(tpl[1]), sin(tpl[2])


def v_cos(tpl: tuple) -> tuple:
    return cos(tpl[0]), cos(tpl[1]), cos(tpl[2])


def gyroid_distance(v: tuple) -> float:
    s_x, s_y, s_z = v_sin(v)
    c_x, c_y, c_z = v_cos(v)

    ds = s_x*c_y+s_y*c_z+s_z*c_x

    return ds


def i_am_a_function(position_vertex: tuple, length: float) -> bool:
    try:
        d = gyroid_distance(
            v_scale(
                position_vertex,
                .1 * gyroid_distance(v_scale(position_vertex, .01))
            )
        )
        return d <= length

    except:
#        print((position_vertex.x, position_vertex.y))
        return False

    # return abs(abs(gyroid_distance(position_vertex)) - 1.) < .5


#def i_am_a_function(position_vertex, depth):
#    return True


def new_node(node: list, function, depth: int):
    global HILBERT_MAP, POINT_ORDER_MAP

    center, direction, length = node

    h_length = length * .5

    new_nodes_list = []
    base_vertex = v_add(center, (h_length, h_length, 0.))

    for i, new_node_dir in enumerate(HILBERT_MAP[direction]):
        x, y = POINT_ORDER_MAP[direction][i]
        # new_center = v_add(
        #     tpl_a=base_vertex,
        #     tpl_b=(x * length), y * length, 0.)
        # )

        new_center = (
            base_vertex[0] + x * length,
            base_vertex[1] + y * length,
            0.
        )

        if function(new_center, length):
            new_nodes_list.append([new_center, new_node_dir, length * .5])

    return new_nodes_list


def hilbert_recursion(l = 80., hilbert_type = "simple", depth = 7, function = i_am_a_function):
    global START_LEAVES

    # initializing the starting nodes
    base_node = START_LEAVES[hilbert_type]
    nodes = []
    for center, orientation, sc in base_node:
        nodes.append([
            tuple([co * l for co in center]),
            orientation,
            l * sc
        ])

    # running the loop
    for i in range(depth):
        new_nodes = []

        for node in nodes:
            output = new_node(node, i_am_a_function, i)

            if any(output):
                new_nodes.extend(output)
            else:
                new_nodes.append(node)

        nodes = new_nodes

    vs = []

    for v, _, _ in nodes:
        vs.append(v)

    return vs


def draw_crv_blender(vs):
    # make a new curve
    crv = data.curves.new('crv', 'CURVE')
    crv.dimensions = '3D'

    # make a new spline in that curve
    spline = crv.splines.new(type='POLY')
    spline.order_u = 0

    # a spline point for each point
    spline.points.add(len(vs)-1) # theres already one point by default

    # assign the point coordinates to the spline points
    for p, new_co in zip(spline.points, vs):
        # p.co = new_co
        p.co = (list(new_co) + [1.0]) # (add nurbs weight)

    # make a new object with the curve
    obj = data.objects.new('object_name', crv)
    context.scene.collection.objects.link(obj)

if __name__ == "__main__":
    vs = hilbert_recursion(hilbert_type="4:3", depth=8)

    print("creating a curve with {} vertexes".format(len(vs)))
    draw_crv_blender(vs)