import spacy
import re
nlp = spacy.load("en_core_web_sm")

dep_file = open("dependency_links.txt", "w")
req_file = open("Requirements_group2.txt", "r")
pattern = r"[A-Za-z][^.!?:]*"
for line in req_file:
    result = re.findall(pattern, line)
    piano_text = result[0]
    piano_doc = nlp(piano_text)
    dep_file.write("{}\n".format(line))
    #tokens = filter(lambda token: token.tag_[0:2] == 'VB' or token.tag_[0:2] == "NN", piano_doc)
    # tokens = filter(lambda token: token.tag_ == 'VB' or token.tag_ ==
    #                 "NN"  or token.tag_ == "VBS" or token.tag_ == "NNS", piano_doc)    
    tokens = piano_doc
    token_dict = {'noun': set(), 'verb': set(), 'verbobj': set(), 'nounphrase': set(), 'coupled_nouns': set(), 'coupled_verbs': set()}
    tokens_to_remove = {'noun': set(), 'verb': set()}
    for token in tokens:
        if token.tag_[0:2] == 'VB':
            if token.dep_ == 'conj':
                text = token.head.text + ' ' +token.text
                token_dict['coupled_verbs'].add(text)
            else:
                token_dict['verb'].add(token.text)
        elif token.tag_[0:2] == 'NN':
            if token.dep_ == 'dobj':
                text = token.head.text + ' ' +token.text
                token_dict['verbobj'].add(text)
                tokens_to_remove['verb'].add(token.head.text)
            elif token.dep_ == 'compound':
                text = token.text + " " + token.head.text
                token_dict['nounphrase'].add(text)
                tokens_to_remove['noun'].add(token.head.text)
            elif token.dep_ == 'pobj':
                if token.head.head.tag_[0:2] == 'NN':
                    continue
                text = token.head.head.text + " " + token.head.text + " " + token.text
                token_dict['verbobj'].add(text)
                tokens_to_remove['verb'].add(token.head.head.text)
            elif token.dep_ == 'conj':
                if token.head.tag_[0:2] == 'VB':
                    text = token.head.text + " " + token.text
                    print(text, 'conj-noun-verb')
                    token_dict['verbobj'].add(text)
                    tokens_to_remove['verb'].add(token.head.text)
                elif token.head.tag_[0:2] == 'NN':
                    if token.head.head.tag_[0:2] == 'VB':
                        text = token.head.head.text + " " + token.head.text + " " + token.text
                        token_dict['verbobj'].add(text)
                        print(text, 'conj-noun-noun-verb')
                        tokens_to_remove['verb'].add(token.head.head.text)
                    else:
                        text = token.head.text + " " + token.text
                        print(text, 'conj-noun-noun')
                        token_dict['coupled_nouns'].add(text)
                        tokens_to_remove['noun'].add(token.head.text)
            else:
                token_dict['noun'].add(token.text)
        dep_file.write(
            f"""
            TOKEN: {token} / Tag: {token.tag_}, Exp: {spacy.explain(token.tag_)} - Link: {token.dep_}, Exp: {spacy.explain(token.dep_)} - Head: {token.head.text}
            \n    """
        )
    #print(token_dict)
    dep_file.write(str(token_dict) + '\n')
    
# Coupled nouns are conjuction of two nouns, we want the artifacts to have both of them while searching
# Coupled verbs are conjuction of two verbs, we want the artifacts to have both of them while searching

# We need to clear duplicate verb and nouns that are part of a noun phrase or verb object
# Idea is to create objects for each noun and verb before we start processing
# for verb-obj-nounX connection found, set noun.verb = verb and set verb inactive, so that it won't be used again
# for nounY-compound-nounX connection, set noun2.compound = noun1, usually compound is on the left
# I expect that nounX will be common in both verb-obj-nounX and nounY-compound-nounX, so we can use that to set the verb and noun



# 1.1.2.9 important to check if noun phrase system is working



''' Can be used to get more information about the tokens

ancestors = [t.text for t in token.ancestors]
children = [t.text for t in token.children]
conjuncts = [t.text for t in token.conjuncts]
lefts = [t.text for t in token.lefts]
rights = [t.text for t in token.rights]
sub_tree = [t.text for t in token.subtree]
dep_file.write(
    f"""
    TOKEN: {token} / Tag: {token.tag_}, Exp: {spacy.explain(token.tag_)} - Link: {token.dep_}, Exp: {spacy.explain(token.dep_)} - Head: {token.head.text}
    \n
        ancestors: {ancestors}\n
        children: {children}\n
        conjuncts: {conjuncts}\n
        lefts: {lefts}\n
        rights: {rights}\n
        subtree: {sub_tree}\n
    """
)
'''