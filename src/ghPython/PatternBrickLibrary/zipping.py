list_1 = [1, 4, 2, 1, 5, 4, 5]
list_2 = ["three", "beer", "15", "17", "kill me now", "no money", "stress"]

list_1, list_2 = zip(*sorted(zip(list_1, list_2)))

print(list_2)
