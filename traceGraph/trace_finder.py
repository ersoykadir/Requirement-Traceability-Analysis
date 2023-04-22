from graph import Graph
import re

# Utility function to search for a keyword in a string.
def find_verbobj_pairs(verb, obj):
    regex = r'\b{0}\s((?:[\w,;:\'\"`]+\s)*){1}\b'.format(verb, obj)
    return re.compile(regex, flags=re.IGNORECASE).search

# \bbuy\s((?:[\w,;:\'\"`]+\s)*)car\b
# ((?:[\w,;:\'\"`]+\s)*){verb}\s?((?:[\w,;:\'\"`]+\s)*){obj}\s?((?:[\w,;:\'\"`]+\s?)*)[\.\n]
# \bemail\saddress\b

# Utility function to search for a keyword in a string.
def findWholeWord(w):
    return re.compile(r'\b{0}\b'.format(w), flags=re.IGNORECASE).search

def find_noun_phrase(noun1, noun2):
    return re.compile(r'\b{0}\s{1}\b'.format(noun1, noun2), flags=re.IGNORECASE).search

def search_keyword(graph, keywords):

    found_nodes = {keyword[0]: set() for keyword in keywords}
    for keyword in keywords:
        for node in graph.issue_nodes.values():
            # if len(node.text) > 10000:
            #     continue
            try:
                keyword_list = keyword[0].split()
                type = keyword[1]
                if type == "nounphrase":
                    match = find_noun_phrase(keyword_list[0], keyword_list[1])(node.text)
                elif type == "verbobj":
                    match = find_verbobj_pairs(keyword_list[0], keyword_list[1])(node.text)
                elif type == "noun" or type == "verb":
                    match = findWholeWord(keyword_list[0])(node.text)
            except Exception as e:
                print(str(e))
                print(node.text)
                print(keywords)
            if match != None:
                # print(match, node.node_id)
                found_nodes[keyword[0]].add(node)

    return found_nodes

    

g = Graph()

keywords = [("guests", "noun"), ("enter username", "verbobj"), ("email address", "nounphrase"), ("password", "noun"), ("signup", "verb")]

nodes = search_keyword(g, keywords)
#sorted_traces = sorted(nodes, key=lambda x: x.node_id)
for keyword in nodes.keys():
    print(keyword)
    print(len(nodes[keyword]))
    for node in nodes[keyword]:
        print(f"{node.node_id} {node.title}\n")
    print('------------------')