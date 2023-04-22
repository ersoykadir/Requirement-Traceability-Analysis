from collections import Counter
import spacy
import re
nlp = spacy.load("en_core_web_sm")
stopwords=set(line.strip() for line in open('SmartStopword.txt'))

def remove_stopwords(tokens):
    return filter(lambda x: x.text not in stopwords, tokens) 

def verb_analysis(token, tokens):
    keywords = []
    for child in token.children:
        if child.dep_ == "acomp" or child.dep_ == "dobj" or child.dep_ == "comp" or child.dep_ == "prt":
            keywords.append(f"""{token.text} {child.text}""")
            #tokens.filter(lambda x: x.text != token.text)
    return keywords

def noun_analysis(token, tokens):
    keywords = []
    for child in token.children:
        if child.dep_ == "compound" or child.dep_ == "nmod":
            keywords.append(f"""{child.text} {token.text}""")
            #tokens.filter(lambda x: x.text != token.text)
    return keywords
    

#opens a text file to write results of tokenizer.
dep_file = open("dependency_links.txt", "w") 

#reads from the Requirements Specification Document.
req_file = open("Requirements_group2.txt", "r")



#Regex pattern to remove numbers of requirement statements.
pattern = r"[A-Za-z][^.!?:()]*"
for line in req_file:
    result = re.findall(pattern, line)
    req_statement = result[0]
    doc = nlp(req_statement)

    #prints the requirement statement.
    dep_file.write("{}\n".format(line))
    #Filters the nouns and verbs from token list for analysis.
    tokens = filter(lambda token: token.tag_ == 'VB' or token.tag_ ==
                    "NN"  or token.tag_ == "VBS" or token.tag_ == "NNS" or token.tag_ == "VBN", doc)
    
    #removes English stopwords from token list.
    tokens = remove_stopwords(tokens)

    for token in tokens:
        if token.tag_ == 'VB' or token.tag_ == 'VBS':
            keywords = verb_analysis(token, tokens)
            if len(keywords):
                dep_file.write(
                    f"""
                    TOKEN: {keywords} / Tag: {token.tag_}, Exp: {spacy.explain(token.tag_)} - Link: {token.dep_}, Exp: {spacy.explain(token.dep_)}
                    \n"""
                )
            else:
                dep_file.write(
                    f"""
                    TOKEN: {token} / Tag: {token.tag_}, Exp: {spacy.explain(token.tag_)} - Link: {token.dep_}, Exp: {spacy.explain(token.dep_)}
                    \n"""
                )
        elif token.tag_ == 'NN' or token.tag_ == 'NNS':
            keywords = noun_analysis(token, tokens)
            if len(keywords):
                dep_file.write(
                    f"""
                    TOKEN: {keywords} / Tag: {token.tag_}, Exp: {spacy.explain(token.tag_)} - Link: {token.dep_}, Exp: {spacy.explain(token.dep_)}
                    \n"""
                )
            else:
                dep_file.write(
                    f"""
                    TOKEN: {token} / Tag: {token.tag_}, Exp: {spacy.explain(token.tag_)} - Link: {token.dep_}, Exp: {spacy.explain(token.dep_)}
                    \n"""
                )
        else:
            dep_file.write(
                    f"""
                    TOKEN: {token} / Tag: {token.tag_}, Exp: {spacy.explain(token.tag_)} - Link: {token.dep_}, Exp: {spacy.explain(token.dep_)}
                    \n"""
             )



