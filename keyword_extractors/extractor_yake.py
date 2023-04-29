import yake
import os

class Extractor:

    def extract(self, text):
        kw_extractor = yake.KeywordExtractor(top=10, stopwords=set(line.strip() for line in open('SmartStopword.txt')))
        keywords = kw_extractor.extract_keywords(text.lower())
        keywords = sorted(keywords, key=lambda x: x[1], reverse=True)
        return keywords

def extract_yake(text, smart_stopwords_path):
        kw_extractor = yake.KeywordExtractor(top=10, stopwords=set(line.strip() for line in open(smart_stopwords_path)))
        keywords = kw_extractor.extract_keywords(text.lower())
        keywords = sorted(keywords, key=lambda x: x[1], reverse=True)
        keywords = [x[0] for x in keywords]
        return keywords