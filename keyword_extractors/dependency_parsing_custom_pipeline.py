import spacy
import re
from collections import Counter

nlp = spacy.load("en_core_web_sm")

def lemmatizer(text):
    tokens = nlp(text)
    for token in tokens:
        text = text.replace(token.text, token.lemma_)
    return text

def most_frequent_words(file, stopwords_path):
    stopwords=set(line.strip().lower() for line in open(stopwords_path))
    complete_text = nlp(file.read())
    words = [
        token.text
        for token in complete_text
        if not token.is_stop and not token.is_punct and not token.is_space
    ]

    for tup in Counter(words).most_common(5):
        stopwords.add(tup[0])

def remove_stopwords(tokens, stopwords_path):
    stopwords=set(line.strip().lower() for line in open(stopwords_path))
    return filter(lambda x: x.text.lower() not in stopwords, tokens) 

def verb_analysis(token, token_dict):
    flag = False
    for child in token.children:
        if child.dep_ == "acomp" or child.dep_ == "dobj" or child.dep_ == "comp" or child.dep_ == "prt":
            token_dict["verb-objects"].append(f"""{token.lemma_} {child.lemma_}""")
            flag = True
    return flag

def noun_analysis(token, token_dict):
    flag = False
    for child in token.children:
        if child.dep_ == "compound" or child.dep_ == "nmod" or child.dep_ == "amod":
            token_dict["noun-objects"].append(f"""{child.lemma_} {token.lemma_}""")
            if child.lemma_ not in token_dict["nouns"]: token_dict["nouns"].append(child.lemma_)
            if token.lemma_ not in token_dict["nouns"]: token_dict["nouns"].append(token.lemma_)
            flag = True
    return flag
    
#Regex pattern to remove numbers of requirement statements.
def custom_extractor(line, stopwords_path):

    pattern = r"[A-Za-z][^.!?:()]*"
    token_dict = {"verbs": [], "verb-objects": [], "nouns": [], "noun-objects":[]}

    result = re.findall(pattern, line)
    req_statement = ' '.join(result)
    doc = nlp(req_statement)

    #dep_file.write("{}\n".format(line))

    #Filters the nouns and verbs from token list for analysis.
    tokens = filter(lambda token: token.tag_[0:2] == 'VB' or token.tag_[0:2] == "NN" , doc)
    
    #removes English stopwords from token list.
    #tokens = remove_stopwords(tokens, stopwords_path)

    for token in tokens:
        if token.tag_[0:2] == 'VB':
            if not verb_analysis(token, token_dict):
                token_dict["verbs"].append(token.lemma_)
        elif token.tag_[0:2] == 'NN':
            if not noun_analysis(token, token_dict):
                token_dict["nouns"].append(token.lemma_)
    return token_dict

print(str(custom_extractor(lemmatizer("1.2.8.4. Created annotations shall be reachable from both profile page and relevant target resource(s)."), "")))
print(lemmatizer("1.2.8.4. Created annotations shall be reachable from both profile page and relevant target resource(s)."))