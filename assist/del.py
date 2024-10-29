import re

desired_length_of_word = 5
size_of_target_file = 27

file = "rooms.txt"
path = "C:\\Users\\alani\\Desktop\\"
target_file = "rooms_edit.txt"

f = open(f'{path}{file}', 'r')
g = open(f'{path}{target_file}', 'w')

for line in f:
    results = [line.strip().lower() for line in f if line]

for item in results:
    print(item)

    newstr = re.match(".*â€“", item)
    if newstr:
        word = newstr[0][0:-4]
    else:
        newstr = re.match(".*–", item)
        if newstr:
            word = newstr[0][0:-2]
        else:
            word = item



    g.write("%s\n" % word)

print(f"FINISHED words_{size_of_target_file}k_{desired_length_of_word}.txt")