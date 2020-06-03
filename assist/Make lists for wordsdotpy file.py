from utils import gut_words, make_dict

def make_lists_for_words_py(n_ers):
    gutted = gut_words(n_ers)
    dict = make_dict(gutted, n_ers)
    print()