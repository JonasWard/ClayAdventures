# split list function
import math


def split_function(input_list, index):

    tolerance = .1

    end = int(math.floor(index))
    start = int(math.ceil(index))

    if index - end < tolerance:

        split_index = end

        list_a = input_list[:split_index + 1]
        list_b = input_list[split_index:]

    elif start - index < tolerance:

        split_index = start

        list_a = input_list[:split_index + 1]
        list_b = input_list[split_index:]

    else:

        list_a = input_list[:start] + [index]
        list_b = [index] + input_list[start:]

    print(list_a, list_b)

a = [i for i in range(10)]

split_function(a, 5.2)