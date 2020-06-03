from utils import gut_words

words = ["hello", "my", "fiend", "you"]

res = list(filter(lambda w : len(w) == 5, words))

print(res)