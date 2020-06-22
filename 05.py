import itertools

a = ["aaa", "bbb", "ccc"]

gen = itertools.permutations(a, 3)

while True:
    print(next(gen))
