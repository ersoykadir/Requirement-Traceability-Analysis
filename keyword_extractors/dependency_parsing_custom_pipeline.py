import spacy
import re
from collections import Counter

nlp = spacy.load("en_core_web_sm")
stopwords=set(line.strip().lower() for line in open('SmartStopword.txt'))

def most_frequent_words(file):
    complete_text = nlp(file.read())
    words = [
        token.text
        for token in complete_text
        if not token.is_stop and not token.is_punct and not token.is_space
    ]

    for tup in Counter(words).most_common(5):
        stopwords.add(tup[0])

def remove_stopwords(tokens):
    return filter(lambda x: x.text.lower() not in stopwords, tokens) 

def verb_analysis(token, token_dict):
    for child in token.children:
        if child.dep_ == "acomp" or child.dep_ == "dobj" or child.dep_ == "comp" or child.dep_ == "prt":
            token_dict["verb-objects"].append(f"""{token.text} {child.text}""")
            return True
    return False

def noun_analysis(token, token_dict):
    for child in token.children:
        if child.dep_ == "compound" or child.dep_ == "nmod" or child.dep_ == "amod":
            token_dict["noun-objects"].append(f"""{child.text} {token.text}""")
            return True
    return False
    

#dep_file = open("dependency_links.txt", "w") 
#req_file = open("Requirements_group2.txt", "r")

#Regex pattern to remove numbers of requirement statements.
def custom_extractor(line):

    pattern = r"[A-Za-z][^.!?:()]*"
    token_dict = {"verbs": [], "verb-objects": [], "nouns": [], "noun-objects":[]}

    result = re.findall(pattern, line)
    req_statement = ' '.join(result)
    doc = nlp(req_statement)

    #dep_file.write("{}\n".format(line))

    #Filters the nouns and verbs from token list for analysis.
    tokens = filter(lambda token: token.tag_[0:2] == 'VB' or token.tag_[0:2] == "NN" , doc)
    
    #removes English stopwords from token list.
    tokens = remove_stopwords(tokens)

    for token in tokens:
        if token.tag_[0:2] == 'VB':
            if not verb_analysis(token, token_dict):
                token_dict["verbs"].append(token.text)
        elif token.tag_[0:2] == 'NN':
            if not noun_analysis(token, token_dict):
                token_dict["nouns"].append(token.text)
    return token_dict
  