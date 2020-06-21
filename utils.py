from collections import Counter
from words import trunk
import random
import copy

def add_desired_and_remove_banned_from_dict(desired_words, banned_words, dict):
    dict2 = copy.deepcopy(dict)
    for desired in desired_words:
        gut = gut_words(desired)[0]
        if gut in dict2.keys() and desired not in dict2[gut]:
            dict2[gut].append(desired)
        else:
            dict2[gut] = [desired]
    for banned in banned_words:
        entry = dict2[gut_words(banned)[0]]
        if banned in entry:
            entry.remove(banned)
            if len(entry) == 0:
                del dict2[gut_words(banned)[0]]
    return dict2
def print_grid(grid):
    print(*grid, sep='\n')
def file_to_list(filename, path):
    with open(f'{path}{filename if isinstance(filename, str) else f"words_{filename[0]}k_{filename[1]}.txt"}', 'r') as f:
        list = f.read().splitlines()
        list_lower = [word.lower() for word in list]
    return list_lower
def gut_words(wordlist):

    if isinstance(wordlist, str):
        wordlist = [wordlist]

    gutted_list = []
    for line in wordlist:
        word = line.strip()
        word_array = []
        for i in range(0, len(wordlist[0]), 2):
            word_array.append(word[i])
        gutted_list.append("".join(word_array))

    # dic = dict(Counter(gutted_list))

    lis = list(set(gutted_list))
    return lis
def ungut_words(gutted_word, wordlist):

    def validate_guts(gutted_word, word):
        if len(gutted_word) == 0:
            return False

        for i in range(len(gutted_word)):
            if gutted_word[i] != word[i*2]:
                return False

        return True

    return [word for word in wordlist if validate_guts(gutted_word, word)]
def make_dict(gut, list):
    dic = {}
    for g in gut:
        dic[g] = ungut_words(g, list)
    return dic
def sum_dicts(a, b):
    for key in b:
        if key in a.keys():
            a[key] = list(set(a[key] + b[key]))
        else:
            a[key] = b[key]
    return a
def prepare_helium(grid_dimension, banned_words, desirable_words, mandatory_words):

    #Filter desired and banned words to only those of wordlength.
    banned_words = list(filter(lambda w : len(w) == grid_dimension, banned_words))
    desirable_words = list(filter(lambda w : len(w) == grid_dimension, desirable_words))
    mandatory_words = list(filter(lambda w : len(w) == grid_dimension, mandatory_words))

    #Fetch the fivers - both WORDS and DICT - from trunk. I say fivers, could be sixers, seveners, etc. Then filter.
    trunk_dict = add_desired_and_remove_banned_from_dict(desirable_words, banned_words, trunk[grid_dimension]["dict"])

    #Shuffle gut list then move DESIRED words to START.
    supergut = list(trunk_dict.keys())
    random.shuffle(supergut)
    random.shuffle(desirable_words)

    for gut in gut_words(desirable_words):
        supergut.remove(gut)
        supergut = [gut] + supergut

    gutted_mand = []
    if bool(mandatory_words):
        gutted_mand = gut_words(mandatory_words)
        supergut = gutted_mand + [gut for gut in supergut if gut not in gutted_mand]
        mand_dic = make_dict(gutted_mand, mandatory_words)
        trunk_dict = sum_dicts(trunk_dict, mand_dic)

    #ye# trunk_words_filtered = sum([word for word in trunk_dict_filtered.values()], [])
    #egh# trunk_words_filtered = list(set(trunk_words).difference(banned_words + desirable_words))
    #hegh# supergut = gutted_desirable_words + [gut for gut in gutted_words_5 if gut not in gutted_desirable_words]

    return {"supergut": supergut, "superdict": trunk_dict, "desirable_words": desirable_words, "gutted_mand": gutted_mand}
# test_data = { "mandatory_words": ["xuxux"], "banned_words": [], "desirable_words_unfiltered": ["bobob", "yoyoy", "qiqiq"], "threshold": 2 }
test_data = { "mandatory_words": ["stream", "roams", "apple"], "banned_words": [], "desirable_words_unfiltered": [], "threshold": 0 }