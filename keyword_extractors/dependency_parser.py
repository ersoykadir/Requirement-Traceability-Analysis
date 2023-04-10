import spacy
import re
nlp = spacy.load("en_core_web_sm")

dep_file = open("dependency_links.txt", "w")
req_file = open("Requirements.txt", "r")
pattern = r"[A-Za-z][^.!?:()]*"
for line in req_file:
    result = re.findall(pattern, line)
    piano_text = result[0]
    piano_doc = nlp(piano_text)
    dep_file.write("{}\n".format(line))
    for token in piano_doc:
        dep_file.write(
        f"""
    TOKEN: {token.text}
    =====
    {token.tag_ = }
    {spacy.explain(token.tag_)}
    {token.head.text = }
    {token.dep_ = }
    {spacy.explain(token.dep_)}\n\n"""
        )
