import operator
import nltk
import re
from rake_nltk import Rake


class Extractor:
    def __init__(self):
        self.pattern = r"[A-Za-z][^\.!?:]*[\.\!?:]"

    def extract(text):
        r = Rake(stopwords=set(line.strip() for line in open('SmartStopword.txt')))
        result = re.findall(pattern, text)
        text = result[0]
        r.extract_keywords_from_text(text.lower())
        return r.get_ranked_phrases()

