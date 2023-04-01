import operator
import nltk
import re
from rake_nltk import Rake

pattern = r"[A-Za-z][^\.!?:]*[\.\!?:]"
sourcefile = open("Extraction_rake.txt", "w")
for line in open("Requirements.txt"):
    r = Rake(stopwords=set(line.strip() for line in open('SmartStopword.txt')))
    result = re.findall(pattern, line)
    text = result[0]
    r.extract_keywords_from_text(text.lower())
    print(text, file=sourcefile)
    print(r.get_ranked_phrases(), file=sourcefile)
    print("\n", file=sourcefile)

sourcefile.close()
