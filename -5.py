import random

def ran(order):
    if len(order) < 3:
        return order[::-1]
    else:
        while order == sorted(order) or order == sorted(order)[::-1]:
            random.shuffle(order)
        return order

print(ran([0, 1, 2]))