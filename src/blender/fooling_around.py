POINT_ORDER_MAP = {
    'S': [(0, 0), (0, 1), (1, 1), (1, 0)],
    'W': [(0, 0), (1, 0), (1, 1), (0, 1)],
    'E': [(1, 1), (0, 1), (0, 0), (1, 0)],
    'N': [(1, 1), (1, 0), (0, 0), (0, 1)]
}

new_dict = {}
for key, values in POINT_ORDER_MAP.items():
    v_list = []
    for a,b in values:
        v_list.append((a-1.,b-1.))

    new_dict[key] = v_list

print(new_dict)

# shifting list
a_list=[
    [(-2.5, -1., 0), 'W', .5],
    [(-2.5, -0., 0), 'S', .5],
    [(-1.5, -0., 0.), 'S', .5],
    [(-1.5, -1., 0.), 'E', .5],
    [(-.5, -1., 0), 'W', .5],
    [(-.5, -0., 0), 'S', .5],
    [(.5, -0., 0.), 'S', .5],
    [(.5, -1., 0.), 'E', .5],
    [(.5, -2., 0.), 'N', .5],
    [(-.5, -2., 0), 'N', .5],
    [(-1.5, -2., 0.), 'N', .5],
    [(-2.5, -2., 0), 'N', .5]
]

for i, (c, _, _) in enumerate(a_list):
    n_c = (c[0]+1, c[1]+1, 0)
    a_list[i][0] = n_c

for entry in a_list:
    print(entry)