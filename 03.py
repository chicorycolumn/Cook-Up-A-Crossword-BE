from itertools import product

a = ["a", "b", "c", "d"]

gen1 = product(a, repeat=3)

dic = {"a": [True], "b": [True, True, True], "c": [True, True], "d": [True, True, True]}

def gut_in_grid_not_more_times_than_it_has_dic_entries(current_guts, dic):
    for gut in current_guts:
     if len(dic[gut]) < current_guts.count(gut):
         return False
    return True

while True:
    current_guts = next(gen1)
    if not gut_in_grid_not_more_times_than_it_has_dic_entries(current_guts, dic):
        print("FAIL", current_guts)
    else:
        print("PASS", current_guts)

# for one in a:
#     for two in a:
#         for three in a:
#             print(one, two, three)