# python -m spacy download en_core_web_sm
import spacy
import re
from string import punctuation

nlp = spacy.load("en_core_web_sm")
nlp.Defaults.stop_words |= set(line.strip() for line in open('SmartStopword.txt'))


def get_hotwords(text):
    result = []
    pos_tag = ['PROPN', 'ADJ', 'NOUN', 'VERB']  # 1
    doc = nlp(text.lower())  # 2
    for token in doc:
        # 3
        if (token.text in nlp.Defaults.stop_words or token.text in punctuation):
            continue
        # 4
        if (token.pos_ in pos_tag):
            result.append(token.text)

    return result  # 5


sourcefile = open("Extraction_spacy.txt", "w")
pattern = r"[A-Za-z][^\.!?:]*[\.\!?:]"
for line in open("Requirements.txt"):
    result = re.findall(pattern, line)
    text = result[0]
    print("text:", text, file=sourcefile)
    results = set(get_hotwords(text))
    print("Result: ", results, file=sourcefile)
    print("\n", file=sourcefile)
