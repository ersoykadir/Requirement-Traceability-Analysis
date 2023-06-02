import spacy
import re
from collections import Counter
import time
nlp = spacy.load("en_core_web_sm")

def lemmatizer(text):
    tokens = nlp(text)
    result = " ".join(token.lemma_ for token in tokens)
    return result

def most_frequent_words(req_file, stopwords_path):
    file = open(req_file, "r", encoding="utf-8")
    complete_text = nlp(file.read())
    words = [
        token.text
        for token in complete_text
        if not token.is_stop and not token.is_punct and not token.is_space
    ]
    f = open(stopwords_path, "a", encoding="utf-8")
    f.write("\n")
    for tup in Counter(words).most_common(5):
        f.write(f"{tup[0]}\n")

def verb_analysis(token, token_dict):
    flag = False
    for child in token.children:
        if child.dep_ == "acomp" or child.dep_ == "dobj" or child.dep_ == "comp" or child.dep_ == "prt":
            token_dict["verb-objects"].append(f"""{token.lemma_.lower()} {child.lemma_.lower()}""")
            flag = True
        if child.dep_ == 'prep':
            for sub_child in child.children:
                if sub_child.dep_ == "pobj":
                    token_dict["verb-objects"].append(f"""{token.lemma_.lower()} {child.lemma_.lower()} {sub_child.lemma_.lower()}""")
                    token_dict["verb-objects"].append(f"""{token.lemma_.lower()} {sub_child.lemma_.lower()}""")
                    flag = True
    return flag

def noun_analysis(token, token_dict):
    flag = False
    compounds = []
    # if token.dep_ == "compound" :
    #     return True
    # if token.dep_ == "conj" and (token.head.dep_ == "dobj" or token.head.dep_ == "pobj"):
    #     return True
    # if token.dep_ == "dobj" or token.dep_ == "pobj":
    #     return True
    for child in token.children:
        if child.dep_ == "nmod" or child.dep_ == "amod":
            token_dict["noun-objects"].append(f"""{child.lemma_.lower()} {token.lemma_.lower()}""")
            if child.lemma_ not in token_dict["nouns"]: token_dict["nouns"].append(child.lemma_.lower())
            if token.lemma_ not in token_dict["nouns"]: token_dict["nouns"].append(token.lemma_.lower())
            flag = True
        if child.dep_ == "compound":
            compounds.append(child.lemma_.lower())
            flag = True
        if child.dep_ == 'prep':
            for sub_child in child.children:
                if sub_child.dep_ == "pobj":
                    token_dict["verb-objects"].append(f"""{token.lemma_.lower()} {child.lemma_.lower()} {sub_child.lemma_.lower()}""")
                    flag = True
        if child.dep_ == 'conj':
            if token.dep_ == 'dobj':
                token_dict["verb-objects"].append(f"""{token.head.lemma_.lower()} {child.lemma_.lower()}""")
                flag = True
            if token.dep_ == 'pobj':
                token_dict["verb-objects"].append(f"""{token.head.head.lemma_.lower()} {child.lemma_.lower()}""")
                flag = True     
    if len(compounds) > 0:
        token_dict["noun-objects"].append(f"""{" ".join(compounds)} {token.lemma_.lower()}""")
        token_dict["nouns"].append(f"""{token.lemma_.lower()}""")
    return flag

def remove_stopwords_from_text(text, stopwords_path):
    stopwords=set(line.strip().lower() for line in open(stopwords_path))
    return " ".join(filter(lambda x: x.lower() not in stopwords, text.split()))

def remove_stopwords(tokens, stopwords_path):
    stopwords=set(line.strip().lower() for line in open(stopwords_path))
    return filter(lambda x: x.text.lower() not in stopwords, tokens) 

def remove_stopwords_from_keywords(tokens, stopwords_path, repo_stopwords_path):
    stopwords=set(line.strip().lower() for line in open(stopwords_path))
    repo_stopwords=set(line.strip().lower() for line in open(repo_stopwords_path))
    combined = stopwords | repo_stopwords
    return list(filter(lambda x: x.lower() not in combined, tokens))

def clean_token_dict(token_dict, stopwords_path, repo_stopwords_path):
    for key in token_dict:
        token_dict[key] = remove_stopwords_from_keywords(token_dict[key], stopwords_path, repo_stopwords_path)
    return token_dict

#Regex pattern to remove numbers of requirement statements.
def custom_extractor(line, stopwords_path, repo_stopwords_path):

    pattern = r"[A-Za-z][^.!?:()]*"
    token_dict = {"verbs": [], "verb-objects": [], "nouns": [], "noun-objects":[]}

    result = re.findall(pattern, line)
    req_statement = ' '.join(result)
    doc = nlp(req_statement)

    #dep_file.write("{}\n".format(line))

    #Filters the nouns and verbs from token list for analysis.
    tokens = filter(lambda token: token.tag_[0:2] == 'VB' or token.tag_[0:2] == "NN" , doc)
    
    # #removes English stopwords from token list.
    # tokens = remove_stopwords(tokens, stopwords_path)
    
    for token in tokens:
        if token.tag_[0:2] == 'VB':
            if not verb_analysis(token, token_dict):
                token_dict["verbs"].append(token.lemma_.lower())
        elif token.tag_[0:2] == 'NN':
            if not noun_analysis(token, token_dict):
                token_dict["nouns"].append(token.lemma_.lower())
    
    clean_token_dict(token_dict, stopwords_path, repo_stopwords_path)
    return token_dict

def extract_keywords(file_name, stopwords_path, repo_stopwords_path):
    file = open(file_name, "r")
    out = open(f"keywords_{file_name}.txt", "w")
    for line in file:
        out.write("{}\n".format(line))
        keywords = custom_extractor(line, stopwords_path, repo_stopwords_path)
        out.write("{}\n".format(keywords))
    file.close()

# extract_keywords("Requirements_group2.txt", "SmartStopword.txt", 'repo_stopwords.txt')