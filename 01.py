from collections import Counter

a = ["a", "b", "c"]

print(any(key for key, tally in Counter(a).items() if tally > 1))


# from threading import Timer
#
# switch = True
#
#
#
# def turn_off():
#     global switch
#     switch = False
#
# t = Timer(2.0, turn_off)
# t.start()
#
# while switch:
#     print(switch)
# print("NO")