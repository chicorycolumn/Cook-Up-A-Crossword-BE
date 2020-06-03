import re

path = ""

desired_length_of_word = 5
size_of_target_file = 27

file = f"wordlist_{size_of_target_file}k.txt"
target_file = f"words_{size_of_target_file}k_{desired_length_of_word}.txt"

f = open(f'{path}{file}', 'r')
g = open(f'{path}{target_file}', 'w')

for line in f:
    results = [line.strip().lower() for line in f if line]

for item in results:
    word = "".join(char for char in item.lower() if re.match('[a-z]', char))
    if len(word) == desired_length_of_word:
        g.write("%s\n" % word)

print(f"FINISHED words_{size_of_target_file}k_{desired_length_of_word}.txt")