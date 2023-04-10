import spacy
from spacy import displacy
import re
nlp = spacy.load("en_core_web_sm")

text= "1.1.2.5. Users shall be able to change their profile picture."
pattern = r"[A-Za-z][^.!?:()]*"
result = re.findall(pattern, text)
piano_text = result[0]
piano_doc = nlp(piano_text)
for token in piano_doc:
   print(
    f"""
TOKEN: {token.text}
=====
{token.tag_ = }
{spacy.explain(token.tag_)}
{token.head.text = }
{token.dep_ = }
{spacy.explain(token.dep_)}\n\n"""
    )
   
displacy.serve(piano_doc, style="dep")
