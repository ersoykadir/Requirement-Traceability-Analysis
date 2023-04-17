import spacy
import re
nlp = spacy.load("en_core_web_sm")

dep_file = open("dependency_links.txt", "w")
req_file = open("Requirements_group2.txt", "r")
pattern = r"[A-Za-z][^.!?:()]*"
for line in req_file:
    result = re.findall(pattern, line)
    piano_text = result[0]
    piano_doc = nlp(piano_text)
    dep_file.write("{}\n".format(line))
    tokens = filter(lambda token: token.tag_ == 'VB' or token.tag_ ==
                    "NN"  or token.tag_ == "VBS" or token.tag_ == "NNS", piano_doc)
    for token in tokens:
        dep_file.write(
            f"""
            TOKEN: {token} / Tag: {token.tag_}, Exp: {spacy.explain(token.tag_)} - Link: {token.dep_}, Exp: {spacy.explain(token.dep_)}
            \n"""
        )
        if token.tag_ == 'VB':
            for t in token.children:
                dep_file.write(
                    f"""
                    children: {t.text} / Tag : {t.tag_}, Exp: {spacy.explain(t.tag_)} - Link: {t.dep_}, Exp: {spacy.explain(t.dep_)}
                    \n"""
                )
