from collections import Counter

def print_grid(grid):
    print(*grid, sep='\n')
def file_to_list(filename, path):
    with open(f'{path}{filename if isinstance(filename, str) else f"words_{filename[0]}k_{filename[1]}.txt"}', 'r') as f:
        list = f.read().splitlines()
        list_lower = [word.lower() for word in list]
    return list_lower
def gut_words(wordlist):
    gutted_list = []
    for line in wordlist:
        word = line.strip()
        word_array = []
        for i in range(0, len(wordlist[0]), 2):
            word_array.append(word[i])
        gutted_list.append("".join(word_array))

    dic = dict(Counter(gutted_list))

    lis = list(set(gutted_list))
    return (lis, dic)
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
def prepare_helium(wordlist_5_unfiltered, banned_words, desirable_words_unfiltered):
    desirable_words = list(set(desirable_words_unfiltered).difference(banned_words))
    (gutted_desirable_words, gutted_desirable_words_dict) = gut_words(desirable_words)

    wordlist_5 = list(set(wordlist_5_unfiltered).difference(banned_words + desirable_words))
    (gutted_words_5, gutted_words_5_dict) = gut_words(wordlist_5)

    superlist = wordlist_5 + desirable_words
    supergut = gutted_desirable_words + [gut for gut in gutted_words_5 if gut not in gutted_desirable_words]
    superdict = make_dict(supergut, superlist)

    return (supergut, superdict, desirable_words)
