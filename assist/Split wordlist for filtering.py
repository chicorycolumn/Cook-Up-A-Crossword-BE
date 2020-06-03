path = ""
file = "words_84k_9"

f = open(f'{path}{file}.txt', 'r')

ff = []

for line in f:
    ff.append(line)

g1 = open(f'{path}{file}-1.txt', 'w')
g2 = open(f'{path}{file}-2.txt', 'w')
g3 = open(f'{path}{file}-3.txt', 'w')
g4 = open(f'{path}{file}-4.txt', 'w')
g5 = open(f'{path}{file}-5.txt', 'w')
g6 = open(f'{path}{file}-6.txt', 'w')
g7 = open(f'{path}{file}-7.txt', 'w')
g8 = open(f'{path}{file}-8.txt', 'w')
g9 = open(f'{path}{file}-9.txt', 'w')
gX = open(f'{path}{file}-X.txt', 'w')
gX1 = open(f'{path}{file}-X1.txt', 'w')
gX2 = open(f'{path}{file}-X2.txt', 'w')
gX3 = open(f'{path}{file}-X3.txt', 'w')
gX4 = open(f'{path}{file}-X4.txt', 'w')

arr = [g1, g2, g3, g4, g5, g6, g7, g8, g9, gX, gX1, gX2, gX3, gX4]

count = 0

for line in ff:
    arr[int(count / 1000)].write(line)
    count += 1