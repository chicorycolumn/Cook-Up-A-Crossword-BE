from threading import Timer

switch = True



def turn_off():
    global switch
    switch = False

t = Timer(2.0, turn_off)
t.start()

while switch:
    print(switch)
print("NO")