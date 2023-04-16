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
                    "NN" or token.tag_ == "NNS" or token.tag_ == "JJ", piano_doc)
    for token in tokens:
        objects = ""
        if (token.dep_ == 'dobj'):
            objects = token.head.text + " " + token.text
        if (token.dep_ == 'compound'):
            objects = token.text + " " + token.head.text
        dep_file.write(
            f"""
            TOKEN: {token.text}
            MODIFIED : {objects} \n
            \n"""
        )
