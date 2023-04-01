import spacy
import re


nlp = spacy.load("en_core_web_sm")
nlp.Defaults.stop_words |= set(line.strip() for line in open('SmartStopword.txt'))

pattern = r"[A-Za-z][^\.!?:]*[\.\!?:]"
sourcefile = open("Extraction_spacy_tagged.txt", "w")
for line in open("Requirements.txt"):
    result = re.findall(pattern, line)
    text = result[0]
    doc = nlp(text)

    print(text, file=sourcefile)
    print("Noun phrases:", [chunk.text for chunk in doc.noun_chunks], file=sourcefile)
    print("Verbs:", [token.lemma_ for token in doc if token.pos_ == "VERB"], file=sourcefile)
    print("\n", file=sourcefile)

