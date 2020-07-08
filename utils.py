from collections import Counter
from words import trunk
import random
import copy

def add_desired_and_remove_banned_from_dict(desired_words, banned_words, dict):
    dict2 = copy.deepcopy(dict)
    for desired in desired_words:
        gut = gut_words(desired, True)[0]
        if gut in dict2.keys() and desired not in dict2[gut]:
            dict2[gut].append(desired)
        else:
            dict2[gut] = [desired]
    for banned in banned_words:
        entry = dict2[gut_words(banned, True)[0]]
        if banned in entry:
            entry.remove(banned)
            if len(entry) == 0:
                del dict2[gut_words(banned, True)[0]]
    return dict2

def print_grid(grid):
    print(*grid, sep='\n')

def file_to_list(filename, path):
    with open(f'{path}{filename if isinstance(filename, str) else f"words_{filename[0]}k_{filename[1]}.txt"}', 'r') as f:
        list = f.read().splitlines()
        list_lower = [word.lower() for word in list]
    return list_lower

def gut_words(wordlist, should_remove_duplicates):

    if isinstance(wordlist, str):
        wordlist = [wordlist]

    gutted_list = []
    for line in wordlist:
        word = line.strip()
        word_array = []
        for i in range(0, len(wordlist[0]), 2):
            word_array.append(word[i])
        gutted_list.append("".join(word_array))

    if should_remove_duplicates:
        return list(set(gutted_list))
    else:
        return list(gutted_list)

def ungut_words(gutted_word, wordlist):

    def validate_guts(gutted_word, word):
        if len(gutted_word) == 0:
            return False

        for i in range(len(gutted_word)):
            if gutted_word[i] != word[i*2]:
                return False

        return True

    return [word for word in wordlist if validate_guts(gutted_word, word)]

def make_dict(gutlist, list):
    dic = {}
    for gut in gutlist:
        dic[gut] = ungut_words(gut, list)
    return dic

def sum_dicts(a, b):
    for key in b:
        if key in a.keys():
            a[key] = list(set(a[key] + b[key]))
        else:
            a[key] = b[key]
    return a

def prepare_helium(data, dimension_is_width, shuffle, supershuffle):
    grid_dimension = 0
    if dimension_is_width:
        grid_dimension = data["grid_width"]
    else:
        grid_dimension = data["grid_height"]

    #Filter desired and banned words to only those of wordlength.
    banned_words = list(filter(lambda w : len(w) == grid_dimension, data["banned_words"]))
    desirable_words = list(filter(lambda w : len(w) == grid_dimension, data["desirable_words_unfiltered"]))
    mandatory_words = list(filter(lambda w : len(w) == grid_dimension, data["mandatory_words"]))

    #Fetch the fivers - both WORDS and DICT - from trunk. I say fivers, could be sixers, seveners, etc. Then filter.
    trunk_dict = add_desired_and_remove_banned_from_dict(desirable_words, banned_words, trunk[grid_dimension]["dict"])

    #Shuffle gut list then move DESIRED words to START.
    supergut = list(trunk_dict.keys())
    random.shuffle(supergut)
    random.shuffle(desirable_words)

    for gut in gut_words(desirable_words, True):
        supergut.remove(gut)
        supergut = [gut] + supergut

    gutted_mand = []
    if bool(mandatory_words):
        gutted_mand = gut_words(mandatory_words, False)
        supergut = gutted_mand + [gut for gut in supergut if gut not in gutted_mand]
        mand_dic = make_dict(gutted_mand, mandatory_words)
        trunk_dict = sum_dicts(trunk_dict, mand_dic)

    return {"supergut": supergut, "superdict": trunk_dict, "desirable_words": desirable_words, "gutted_mand": gutted_mand, "mand_words_filtered": mandatory_words}

test_data = { "grid_width": 5, "grid_height": 5, "mandatory_words": [], "banned_words": [], "desirable_words_unfiltered": [], "threshold": 0 }

def make_dict_from_scratch(wordlength):
    return(make_dict(gut_words(trunk[wordlength]["words"], True), trunk[wordlength]["words"]))

def is_A_not_fully_contained_by_B(a, b):
    aa = Counter(a)
    bb = Counter(b)
    aa.subtract(bb)
    in_A_but_not_in_B = [key for key, tally in aa.items() if tally > 0]
    return bool(len(in_A_but_not_in_B))

def does_putative_grid_truly_meet_desithreshold(threshold, bank, desirable_combined, mandatory_words):

    ref = {}

    for word in desirable_combined + mandatory_words:
        ref[word] = False

    for coord in bank.keys():
        continuing = True
        mand_intersection = list(set(bank[coord]["ungutted"]).intersection(mandatory_words))
        if bool(len(mand_intersection)):
            for word in mand_intersection:
                if not ref[word]:
                    ref[word] = True
                    continuing = False
                    break

        if continuing:
            desi_intersection = list(set(bank[coord]["ungutted"]).intersection(desirable_combined))
            if bool(len(desi_intersection)):
                for word in desi_intersection:
                    if not ref[word]:
                        ref[word] = True
                        break

    return len(list(filter(lambda word : ref[word] and word in desirable_combined, ref.keys()))) >= threshold