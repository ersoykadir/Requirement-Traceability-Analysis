from traceGraph import Graph
import re
import sys
sys.path.append('..')
from keyword_extractors.dependency_parsing_custom_pipeline import custom_extractor

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

def find_trace(graph, keyword):
    found_nodes = set()
    for node in graph.issue_nodes.values():
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
        if match != None:
            # print(match, node.node_id)
            found_nodes.add(node)
    return found_nodes
def search_keyword(graph, keywords):

    found_nodes = {}
    for keyword in keywords['verbs']:
        found_nodes[keyword] = find_trace(graph, (keyword, "verb"))
    for keyword in keywords['verb-objects']:
        found_nodes[keyword] = find_trace(graph, (keyword, "verbobj"))
    for keyword in keywords['nouns']:
        found_nodes[keyword] = find_trace(graph, (keyword, "noun"))
    for keyword in keywords['noun-objects']:
        found_nodes[keyword] = find_trace(graph, (keyword, "nounphrase"))
    return found_nodes

import time
def main():
    start = time.time()
    repo_number = sys.argv[1]
    g = Graph(repo_number)
    trace_file = open(f"trace_links_group{repo_number}.txt", "w", encoding="utf-8") 
    req_file = open(f"data_group{repo_number}/group{repo_number}_requirements.txt", "r", encoding="utf-8")

    for line in req_file:
        token_dict = custom_extractor(line, "../keyword_extractors/SmartStopword.txt")
        trace_file.write("{}".format(line))
        trace_file.write("{}\n".format(token_dict))

        nodes = search_keyword(g, token_dict)
        #sorted_traces = sorted(nodes, key=lambda x: x.node_id)
        for keyword in nodes.keys():
            trace_file.write(keyword + ' ' + str(len(nodes[keyword])) + "\n")
            for node in nodes[keyword]:
                try:
                    trace_file.write(f"{node.node_id} {node.title}\n")
                except Exception as e:
                    print(str(e))
                    #print(node.text)
                    print(node.node_id)
            trace_file.write('------------------' + '\n')
        trace_file.write('\n')
    trace_file.close()
    req_file.close()
    end = time.time()
    print(f"Time elapsed: {end - start}")

if __name__ == "__main__":
    main()