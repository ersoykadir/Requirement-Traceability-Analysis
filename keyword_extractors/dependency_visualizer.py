import spacy
from spacy import displacy
import re
nlp = spacy.load("en_core_web_sm")

text= "1.1.3.3.3. Users shall be able to post comments on events which they attended."
pattern = r"[A-Za-z][^.!?:()]*"
result = re.findall(pattern, text)
piano_text = result[0]
piano_doc = nlp(piano_text)
for token in piano_doc:
    children = [child for child in token.children]
    print(
    f"""
TOKEN: {token.text}
=====
{token.tag_ = }
{spacy.explain(token.tag_)}
{token.head.text = }
{token.dep_ = }
{spacy.explain(token.dep_)}
{children = }\n\n"""
    )
   
# displacy.serve(piano_doc, style="dep")
img = displacy.render(piano_doc, style="dep")
with open("dependency_tree.png", "w", encoding="utf-8") as f:
    f.write(img)
