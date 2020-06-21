gridguts = {"across": [10, 20], "down": [11, 22, 33]}
bank = {}

coord_count = 1
for word in gridguts["down"]:
    bank[str(coord_count) + "do"] = word
    coord_count+=1
bank["1ac"] = gridguts["across"][0]
for word in gridguts["across"][1:]:
    bank[str(coord_count) + "ac"] = word
    coord_count+=1

for key in bank.keys():
    print(key)