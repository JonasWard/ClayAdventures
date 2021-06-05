from bpy import ops, data, types, context
from math import sin, cos, acos
import time

# trying to make some differential growth work

DISTANCE = 2.
GRID_SIZE = DISTANCE * 2.
CHAR_LIST = "()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_`abcdefghijklmnopqrstuvwxyz{|}~"
# CHAR_LIST = "012345678"
BASE_PT = (-50., -50., 0.)

START_TIME = time.time()


def time_function(txt: str):
    global START_TIME

    print(txt + ": " + str(time.time() - START_TIME))
    START_TIME = time.time()


# vertex math
def v_add(tpl_a: tuple, tpl_b: tuple) -> tuple:
    return (
        tpl_a[0] + tpl_b[0],
        tpl_a[1] + tpl_b[1],
        tpl_a[2] + tpl_b[2]
    )


def v_sub(tpl_a: tuple, tpl_b: tuple) -> tuple:
    return (
        tpl_a[0] - tpl_b[0],
        tpl_a[1] - tpl_b[1],
        tpl_a[2] - tpl_b[2]
    )


def v_scale(tpl_a: tuple, value: tuple) -> tuple:
    return (
        tpl_a[0] * value,
        tpl_a[1] * value,
        tpl_a[2] * value
    )


def v_len(tpl_a: tuple) -> float:
    return (tpl_a[0] ** 2 + tpl_a[1] ** 2 + tpl_a[2] ** 2) ** .5


def v_distance(tpl_a: tuple, tpl_b: tuple) -> tuple:
    return v_len(v_sub(tpl_a, tpl_b))


def v_sin(tpl: tuple) -> tuple:
    return sin(tpl[0]), sin(tpl[1]), sin(tpl[2])


def v_cos(tpl: tuple) -> tuple:
    return cos(tpl[0]), cos(tpl[1]), cos(tpl[2])


def v_round(tpl: tuple) -> tuple:
    global GRID_SIZE, BASE_PT

    tpl = v_sub(tpl, BASE_PT)

    x = int(round(tpl[0] / GRID_SIZE))
    y = int(round(tpl[1] / GRID_SIZE))
    z = int(round(tpl[2] / GRID_SIZE))

    return (x, y, z)


def v_mid(tpl_a: tuple, tpl_b: tuple) -> tuple:
    v = v_sub(tpl_b, tpl_a)
    return v_add(tpl_a, v_scale(v, .5))


def v_angle(tpl_a: tuple, tpl_b: tuple) -> float:
    xa, ya, _ = v_scale(tpl_a, 1. / v_len(tpl_a))
    xb, yb, _ = v_scale(tpl_b, 1. / v_len(tpl_b))

    cosine = (xa * xb + ya * yb)

    if cosine < 1. and cosine > -1.:
        angle = acos((xa * xb + ya * yb))
    else:
        angle = 3.1415927

    return angle


def v_hash(tpl: tuple) -> str:
    global CHAR_LIST

    x, y, z = v_round(tpl)

    return CHAR_LIST[x] + CHAR_LIST[y] + CHAR_LIST[z]


def v_hash_neighbours(tpl: tuple) -> str:
    global CHAR_LIST

    x, y, z = v_round(tpl)
    index_list = []
    for i in range(-1, 2, 1):
        for j in range(-1, 2, 1):
            index_list.append([x - i, y - j, z])

    char_list = []
    for i, j, k in index_list:
        char_list.append(CHAR_LIST[i] + CHAR_LIST[j] + CHAR_LIST[k])

    return char_list


def v_hash_dict() -> dict:
    global CHAR_LIST

    new_dict = {}
    for cx in CHAR_LIST:
        for cy in CHAR_LIST:
            new_dict[cx + cy + CHAR_LIST[0]] = []

    return new_dict


def v_dot(a: tuple, b: tuple) -> float:
    ax, ay, az = a
    bx, by, bz = b

    d = ax * bx + ay * by + az * bz
    return d


def v_norm(a, b):
    return 1 - abs(v_dot(a, b))


def simple_distance(vs: list) -> dict:
    global DISTANCE

    neighbours = {}

    for i, v in enumerate(vs):
        n_list = []
        for j, v_bis in enumerate(vs):
            d = v_distance(v, v_bis)
            if d <= DISTANCE and not (d < .001):
                n_list.append(v_bis)

        neighbours[v] = n_list

    return neighbours


def hash_distance(vs: list) -> dict:
    global DISTANCE

    hash_dict = v_hash_dict()

    # putting points in corresponding dict key
    for v in vs:
        hash_dict[v_hash(v)].append(v)

    neighbours = {}

    # calculating dict
    for i, v in enumerate(vs):
        v_nbs = v_hash_neighbours(v)
        v_biss = []
        n_list = []

        for hsh in v_nbs:
            v_biss.extend(hash_dict[hsh])

        for v_bis in v_biss:
            d = v_distance(v, v_bis)
            if d <= DISTANCE and not (d < .001):
                n_list.append(v_bis)

        neighbours[v] = n_list

    return neighbours


class GrowingChain:
    def __init__(self, bpts, repulse_mag=.1, repulse_dis=5., attract_mag=.25, goal_len=1.):
        self.vs = bpts
        self.rmv = repulse_mag
        self.amv = attract_mag
        self.rdi = repulse_dis
        self.gll = goal_len
        self.sll = goal_len * 2.
        self.ang = 2.5
        self.rnd = .95

        self._grow_count = 0

    def repulse(self):
        global DISTANCE
        v_pairs = hash_distance(self.vs)

        n_vs = []
        for v, related in v_pairs.items():
            v_sum = tuple(v)
            for v_r in related:
                d = v_distance(v_r, v_sum)

                if d <= self.rdi:
                    scale_val = abs(1. - d / self.rdi)
                    scale_val = 1. if scale_val > 1 else (1. - d / self.gll)
                    v_mv = v_scale(v_sub(v_r, v), scale_val * self.rmv)

                    v_sum = v_add(v_sum, v_mv)

            n_vs.append(v_sum)

        self.vs = n_vs

    def attract(self):
        n_vs = []
        for i in range(len(self.vs)):
            p = self.vs[(i - 1) % len(self.vs)]
            t = self.vs[i]
            n = self.vs[(i + 1) % len(self.vs)]

            d = v_distance(p, t)
            scale_val = abs(1. - d / self.gll)
            scale_val = 1. if scale_val > 1 else (1. - d / self.gll)
            v_mv_p = v_scale(v_sub(p, t), scale_val * self.amv)

            d = v_distance(n, t)
            scale_val = abs(1. - d / self.gll)
            scale_val = 1. if scale_val > 1 else (1. - d / self.gll)
            v_mv_n = v_scale(v_sub(n, t), scale_val * self.amv)

            n_vs.append(v_add(v_add(v_mv_n, t), v_mv_p))

        self.vs = n_vs

    def split(self):
        n_vs = []
        for i in range(len(self.vs)):
            p = self.vs[(i - 1) % len(self.vs)]
            t = self.vs[i]

            d = v_distance(p, t)
            if d >= self.sll:
                n_vs.append(v_mid(p, t))

            n_vs.append(t)

        self.vs = n_vs

    def random_extras(self):
        n_vs = []
        for i in range(len(self.vs)):
            rnd = random.random()
            t = self.vs[i]
            if rnd >= self.rnd:
                p = self.vs[(i - 1) % len(self.vs)]

                n_vs.append(v_mid(p, t))

            n_vs.append(t)

        self.vs = n_vs

    def angling(self):
        n_vs = []
        for i in range(len(self.vs)):
            p = self.vs[(i - 1) % len(self.vs)]
            t = self.vs[i]
            n = self.vs[(i + 1) % len(self.vs)]

            angle = v_norm(v_sub(p, t), v_sub(n, t))

            if angle < self.ang:
                n_vs.append(v_mid(p, t))
                n_vs.append(v_mid(n, t))
            else:
                n_vs.append(t)

        self.vs = n_vs

    def grow(self):
        self.split()
        self.angling()
        self.random_extras()
        self.repulse()
        self.attract()

        self._grow_count += 1

    def __repr__(self):
        return "GrowingChain with {} vertices, grown {} times".format(len(self.vs), self._grow_count)


def test_function(cnt=5):
    import random

    print("---- iteration {} ----".format(cnt))

    vs = []
    for i in range(cnt):
        for j in range(cnt):
            x = (random.random() - .5) * 20.
            y = (random.random() - .5) * 20.
            vs.append((x, y, 0.))

    print("running {} points".format(len(vs)))
    time_function("initializing points")

    hshs = [v_hash(v) for v in vs]
    time_function("generating hashes")
    hshs_ns = [v_hash_neighbours(v) for v in vs]
    time_function("generating hash neighborhood")

    simple_d_dict = simple_distance(vs)
    time_function("calculating simple distance")
    hash_d_dict = hash_distance(vs)
    time_function("calculating hash distances")

    items = {}
    total_dev = 0
    total_pairs = 0
    for key in simple_d_dict.keys():
        deviation = 0
        total_pairs += len(simple_d_dict[key])
        for v in simple_d_dict[key]:
            if not (v in hash_d_dict[key]):
                deviation += 1

        if deviation != 0:
            print("key: " + str(key))
            print("simple dict: " + str(simple_d_dict[key]))
            print("hash dict: " + str(hash_d_dict[key]))

        total_dev += deviation
        items[key] = deviation

    print("total pairs: {}".format(total_pairs))
    print("total deviation: {}".format(total_dev))
    # print(items)
    print(len(v_hash_dict()))


def draw_crv_blender(vs):
    # make a new curve
    crv = data.curves.new('crv', 'CURVE')
    crv.dimensions = '3D'

    # make a new spline in that curve
    spline = crv.splines.new(type='POLY')
    spline.order_u = 0

    # a spline point for each point
    spline.points.add(len(vs) - 1)  # theres already one point by default

    # assign the point coordinates to the spline points
    for p, new_co in zip(spline.points, vs):
        # p.co = new_co
        p.co = (list(new_co) + [1.0])  # (add nurbs weight)

    # make a new object with the curve
    obj = data.objects.new('object_name', crv)
    context.scene.collection.objects.link(obj)


def v_circle(cnt, radius=5.):
    vs = []

    for i in range(cnt):
        alfa = i * 3.141527 * 2. / cnt
        vs.append((
            (cos(alfa) + (random.random() - .5) * .1) * radius,
            (sin(alfa) + (random.random() - .5) * .1) * radius,
            0.
        ))

    return vs


if __name__ == "__main__":
    import random

    cnt = 2

    vs = []
    for i in range(cnt):
        for j in range(cnt):
            x = (random.random() - .01) * 5.
            y = (random.random() - .01) * 5.
            vs.append((x, y, 0.))

    vs = v_circle(20, 5.)
    print(vs)

    gc = GrowingChain(vs, .025, .5, .1, .5)
    draw_crv_blender(gc.vs)
    for i in range(200):
        #        try:
        gc.grow()
        draw_crv_blender(gc.vs)
        #        except:
        #            print("failed")
        ##            print(gc.vs)
        #            break
        print(gc)