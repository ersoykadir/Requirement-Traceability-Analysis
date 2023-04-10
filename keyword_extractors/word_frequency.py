import spacy
from collections import Counter

def most_frequent_words():
    nlp = spacy.load("en_core_web_sm")
    file = open("Requirements.txt", "r")
    complete_text = nlp(file.read())

    words = [
        token.text
        for token in complete_text
        if not token.is_stop and not token.is_punct
    ]

    return Counter(words).most_common(15)

print(most_frequent_words())
