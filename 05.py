a = [1, 2, 3]
b = [3, 4, 5]
c = [2, 4, 6, 8, 10]

x = set(set(a + b)).difference(c)


print(x)