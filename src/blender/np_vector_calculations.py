import numpy as np
import random, time
from differential_growth import *

START_TIME = time.time()


def v_gen_list(count):
    vs = []

    for i in range(count):
        v = []
        for j in range(3):
            v.append(random.random())

        vs.append(tuple(v))

    return vs


def v_addition_test(count=1000000):
    vs_a = v_gen_list(count)
    vs_b = v_gen_list(count)

    vs = []

    time_function("v_generation")
    for a, b in zip(vs_a, vs_b):
        vs.append(v_add(a, b))
    time_function("run the v_addition_test")

    l = 0.
    for v in vs:
        l += v_len(v)
    time_function("run the v len_test: {}".format(l))
    print(vs[0])


def np_gen_list(count):
    vs = []

    for i in range(count):
        vs.append(np.random.random(3))

    return vs


def np_addition_test(count=1000000):
    vs_a = np.array(np_gen_list(count))
    vs_b = np.array(np_gen_list(count))

    time_function("np_generation")
    vs = vs_a + vs_b

    time_function("run the np_addition_test")

    ls = np.linalg.norm(vs, ord=1)
    mass_addition = ls.sum()

    time_function("run the np len_test: {}".format(mass_addition))
    print(vs.shape)
    print(vs[0])


if __name__ == "__main__":
    a_vec = np.random.random(3)
    b_vec = np.random.random(3)

    print(a_vec, b_vec)
    print(a_vec + b_vec)

    v_addition_test(100000)

    np_addition_test(100000)

    cnt = 200

    l = 0.
    for i in range(cnt):
        for j in range(cnt):
            for k in range(cnt):
                l += v_len(((i+.5)/200., (j+.5)/200., (k+.5)/200.))

    print(l / (cnt ** 3))


