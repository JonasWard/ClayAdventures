import time
import numpy as np

def time_f(txt: str):
    global start_time
    print(txt + str(time.time() - start_time))

x = np.random.random((10000000))
y = np.random.random((10000000))
z = np.random.random((10000000))

start_time = time.time()
array_1D = np.random.random((30000000))
time_f("init array_1D: ")
array_3D = np.random.random((10000000, 3))
time_f("init array_3D: ")
np.cos(array_1D)
time_f("cos array_1D: ")
np.cos(array_3D)
time_f("cos array_3D: ")
array_composed = np.array([x, y, z])
time_f("composing array_3D: ")
np.cos(array_composed)
time_f("cos composed array_3D: ")