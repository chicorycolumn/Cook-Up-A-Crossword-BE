from utils import gut_words
import copy

# dict = {"bgt": ["begat", "beget", "bxgxt"], "xxx": ["xxxxx"]}
#
# banned_words = ["bxgxt", "xxxxx"]
# desired_words = ["bogot", "kinky"]
#

dic = {1: ["one"], 2: ["two"], 3: ["three"]}

key = 22

dic2 = {key: "yo"}.update(dic)

print(dic2)