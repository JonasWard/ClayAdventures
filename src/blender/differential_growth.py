from bpy import ops, data, types, context
from math import sin, cos, acos, floor
import time, random

# trying to make some differential growth work

DISTANCE = 2.
GRID_SIZE = DISTANCE * 2.
# long
#CHAR_LIST = " !#'$%&()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_`abcdefghijklmnopqrstuvwxyz{|}~€¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ"
# short
CHAR_LIST = " !#'$%&()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_`abcdefghijklmnopqrstuvwxyz{|}~"
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


def v_norm(a: tuple, b: tuple) -> float:
    return 1 - abs(v_dot(a, b))


def v_unit(a: tuple) -> tuple:
    l = v_len(a)
    return a[0] / l, a[1] / l, a[2] / l


def v_hash_dict() -> dict:
    global CHAR_LIST

    new_dict = {}
    for cx in CHAR_LIST:
        for cy in CHAR_LIST:
            new_dict[cx + cy + CHAR_LIST[0]] = []

    return new_dict


def v_round(v: tuple, d_invert: float, c: tuple) -> tuple:
    x, y, z = v_scale(v_sub(v, c), d_invert)

    x = int(floor(x))
    y = int(floor(y))
    z = int(floor(z))

    return (x, y, z)


def v_hash(v: tuple, d_invert: float, c: tuple) -> str:
    global CHAR_LIST

    x, y, z = v_round(v, d_invert, c)

    return CHAR_LIST[x] + CHAR_LIST[y] + CHAR_LIST[z]


def v_hash_neighbours(v: tuple, d_invert: float, c: tuple) -> str:
    global CHAR_LIST

    x, y, z = v_round(v, d_invert, c)

    x = int(floor(x))
    y = int(floor(y))
    z = int(floor(z))

    index_list = []
    for i in range(-1, 2, 1):
        for j in range(-1, 2, 1):
            index_list.append([x - i, y - j, z])

    char_list = []
    for i, j, k in index_list:
        char_list.append(CHAR_LIST[i] + CHAR_LIST[j] + CHAR_LIST[k])

    return char_list


def v_hash_distance(vs:list, d: float, c: tuple) -> dict:
    hash_dict = v_hash_dict()

    d_invert = 1. / d

    # putting points in corresponding dict key
    for v in vs:
        hash_dict[v_hash(v, d_invert, c)].append(v)

    neighbours = {}

    # calculating dict
    for i, v in enumerate(vs):
        v_nbs = v_hash_neighbours(v, d_invert, c)
        v_biss = []
        n_list = []

        for hsh in v_nbs:
            v_biss.extend(hash_dict[hsh])

        for v_bis in v_biss:
            d = v_distance(v, v_bis)
            if d <= d and not (d < .001):
                n_list.append(v_bis)

        neighbours[v] = n_list

    return neighbours


def circle(cnt=20, r=5.):
    vs = []
    dl = 3.1415927 * 2. / cnt

    for i in range(cnt):
        alpha = dl * i

        vs.append((
            cos(alpha) * (r + random.random()),
            sin(alpha) * (r + random.random()),
            0.
        ))

    return vs


def curtailed_LennordJones_potential(r0, D, r1=2., max_val=3.) -> float:
    if D > r1:
        return 0.

    s_over_r = r0 / D
    v = (s_over_r ** 12 - s_over_r ** 6)

    if v > max_val:
        return max_val

    return v


def LennordJones_potential(r0, D):
    s_over_r = r0 / D

    return (s_over_r ** 12 - s_over_r ** 6)


def plot_LennordJones_potential(r0, sampling=200):
    delta = 3. / sampling

    vs = []

    for i in range(1, sampling + 1):
        vs.append((i * delta, LennordJones_potential(r0, i * delta), 0.))

    return vs


def v_bounds(vs: list) -> list:
    x, y, z = zip(*vs)

    return [
        (min(x), max(x)),
        (min(y), max(y)),
        (min(z), max(z))
    ]


class Growth:
    def __init__(self, vs, rep, att, rr, ar, jr, sm, ri):
        self.vs = vs
        self.rep = rep
        self.att = att
        self.rr = rr
        self.ar = ar
        self.sr = ar * 2.
        self.jr = jr
        self.sm = sm
        self.ri = ri

        self._length_dict = {}
        self._treshold_repulse_count = 15
        self._growth_count = 0

    def jiggle(self):
        n_vs = []
        for v in self.vs:
            alpha = random.random() * 3.1415927 * 2.
            r = random.random() * self.jr

            n_vs.append(v_add(
                v,(
                    cos(alpha) * r,
                    sin(alpha) * r,
                    0.
                )))

        self.vs = n_vs

    def random_insert(self):
        n_vs = []
        for i in range(len(self.vs)):
            v = self.vs[i]

            n_vs.append(v)
            if random.random() > self.ri and self._length_dict[v] < self._treshold_repulse_count:
                n = self.vs[(i + 1) % len(self.vs)]
                n_vs.append(v_scale(v_add(v, n), .5))

        self.vs = n_vs

    def smoothing(self):
        n_vs = []
        for i in range(len(self.vs)):
            p = self.vs[(i - 1) % len(self.vs)]
            v = self.vs[i]
            n = self.vs[(i + 1) % len(self.vs)]

            vm = v_sub(v_scale(v_add(v, p), .5), v)
            v = v_add(v, v_scale(vm, self.sm))

            n_vs.append(v)

        self.vs = n_vs

    def split(self):
        n_vs = []
        for i in range(len(self.vs)):
            v = self.vs[i]
            n = self.vs[(i + 1) % len(self.vs)]

            n_vs.append(v)
            if v_distance(v, n) > self.sr:
                n_vs.append(v_scale(v_add(v, n), .5))

        self.vs = n_vs

    def repulsion(self):
        c = self.center()
        v_dict = v_hash_distance(self.vs, self.rr, c)
        n_vs = []

        self._length_dict = {}

        for va, ovs in v_dict.items():
            vm = (0., 0., 0.)
            for v in ovs:
                d = v_distance(v, va)

                if d < self.rr:
                    sc = self.rep * (1. - d / self.rr) ** 2.
                    vm_loc = v_scale(v_sub(va, v), sc)
                    vm = v_add(vm, vm_loc)

            va = v_add(va, vm)
            self._length_dict[va] = len(ovs)
            n_vs.append(va)

        self.vs = n_vs

    def attraction(self):
        n_vs = []
        for i in range(len(self.vs)):
            p = self.vs[(i - 1) % len(self.vs)]
            v = self.vs[i]
            n = self.vs[(i + 1) % len(self.vs)]

            pv = v_sub(p, v)
            pv_l = v_len(pv)
            vm = v_scale(pv, self.att * (pv_l - self.ar - pv_l))
            nv = v_sub(n, v)
            nv_l = v_len(nv)
            vm = v_add(vm, v_scale(nv, self.att * (nv_l - self.ar - nv_l)))

            n_vs.append(v_add(v, vm))

        self.vs = n_vs

    def grow(self):
        self.split()
        self.attraction()
        self.repulsion()
        self.random_insert()
        self.jiggle()
        self.smoothing()

        self._growth_count += 1

    def plg(self):
        draw_crv_blender(self.vs)

    def center(self) -> tuple:
        (x_min, x_max), (y_min, y_max), (z_min, z_max) = v_bounds(self.vs)
        return (x_min - 1., y_min, - 1., z_min - 1.)

    def bounds(self):
        return v_bounds(self.vs)

    def area(self):
        (x_min, x_max), (y_min, y_max), _ = v_bounds(self.vs)

        return (x_max - x_min) * (y_max - y_min)

    def __repr__(self):
        return "Growth with {} Vertexes, grown {} times".format(len(self.vs), self._growth_count)


# def test_function(cnt=5):
#     import random
#
#     print("---- iteration {} ----".format(cnt))
#
#     vs = []
#     for i in range(cnt):
#         for j in range(cnt):
#             x = (random.random() - .5) * 20.
#             y = (random.random() - .5) * 20.
#             vs.append((x, y, 0.))
#
#     print("running {} points".format(len(vs)))
#     time_function("initializing points")
#
#     hshs = [v_hash(v) for v in vs]
#     time_function("generating hashes")
#     hshs_ns = [v_hash_neighbours(v) for v in vs]
#     time_function("generating hash neighborhood")
#
#     simple_d_dict = simple_distance(vs)
#     time_function("calculating simple distance")
#     hash_d_dict = hash_distance(vs)
#     time_function("calculating hash distances")
#
#     items = {}
#     total_dev = 0
#     total_pairs = 0
#     for key in simple_d_dict.keys():
#         deviation = 0
#         total_pairs += len(simple_d_dict[key])
#         for v in simple_d_dict[key]:
#             if not (v in hash_d_dict[key]):
#                 deviation += 1
#
#         if deviation != 0:
#             print("key: " + str(key))
#             print("simple dict: " + str(simple_d_dict[key]))
#             print("hash dict: " + str(hash_d_dict[key]))
#
#         total_dev += deviation
#         items[key] = deviation
#
#     print("total pairs: {}".format(total_pairs))
#     print("total deviation: {}".format(total_dev))
#     # print(items)
#     print(len(v_hash_dict()))


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

START_TIME = time.time()

def time_function(txt: str):
    global START_TIME

    print(txt + ' : ' + str(time.time() - START_TIME))
    START_TIME = time.time()


if __name__ == "__main__":
    vs = circle(80, 5.)

    local_time = time.time()

    gc = Growth(
        vs,
        rep=.5,
        att=.15,
        rr=1.5,
        ar=1.,
        jr=.2,
        sm=.7,
        ri=.995
    )

    plgs = [gc.plg()]
    perf_per_v_treshold = 2000
    vertex_treshold = 5000
    perf_treshold_cnt = 0

    for i in range(10000):
        gc.grow()
        lc_time = time.time() - local_time
        local_time = time.time()
        perf_val = round(len(gc.vs) / lc_time)
        if perf_val < perf_per_v_treshold:
            perf_treshold_cnt += 1
        else:
            perf_treshold_cnt = 0

        if (perf_treshold_cnt > 3 and len(gc.vs) > 100) or len(gc.vs) > vertex_treshold:
            break

#        plgs.append(gc.plg())
        if i % 100 == 0:
            time_function("loop {}".format(i))
            print("growth area: {}".format(gc.area()))
            print(str(gc) + '\n')

        elif i % 5 == 0:
            print('\b{} - {}, '.format(len(gc.vs), perf_val))
    # plgs.reverse()

    gc.plg()