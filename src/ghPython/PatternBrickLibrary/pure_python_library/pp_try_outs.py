#trying out the vector class

from pp_vector import Vector3D

v_a = Vector3D(0)
v_b = Vector3D(1.0, 1.0)
v_c = Vector3D(2.0, 3.0, 4.0)
v_d = Vector3D([1.1, 1.2, 2.3])
v_e = Vector3D((1.7, .7, 1.4))
v_e_bis = Vector3D(v_e)
v_f = Vector3D((1.0, .0, .0))

v_list = [v_a, v_b, v_c, v_d, v_e, v_e_bis, v_f]

print("coordinates:")
[print(entry) for entry in v_list]
print("lengths:")
[print(entry.length) for entry in v_list]
print("angles:")
[print(entry.angle2D) for entry in v_list]
print("angles2D:")
print(v_d.angle_vec(v_e))
print(v_e.angle_vec(v_e))
print(v_e.angle_vec(v_f))
