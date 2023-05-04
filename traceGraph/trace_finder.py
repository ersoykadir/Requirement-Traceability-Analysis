"""
Kadir Ersoy - Ecenur Sezer
Requirements Traceability Tool

Creates traces from requirements to other artifacts using a custom keyword extractor and regex matching.
Writes traces to a file.
"""


import re, sys
from traceGraph import Graph
sys.path.append('..')
from keyword_extractors.dependency_parsing_custom_pipeline import custom_extractor

# Regular expressions to search for keywords in text.
word_regex = r'\b{0}\b'
verbobj_regex = r'\b{0}\s((?:[\w,;:\'\"`]+\s)*){1}\b'
noun_phrase_regex = r'\b{0}\s{1}\b'

def find_trace(graph, regex):
    found_nodes = set()
    compiled_regex = re.compile(regex, flags=re.IGNORECASE)
    for node in graph.issue_nodes.values():
        try:
            match = compiled_regex.search(node.text)
        except Exception as e:
            print(str(e))
            print(node.text)
        if match != None:
            # print(match, node.node_id)
            found_nodes.add(node)
    return found_nodes

def search_keyword(graph, keyword_list):

    found_nodes = {}
    for keyword in keyword_list['verbs']:
        regex = word_regex.format(keyword)
        found_nodes[keyword] = find_trace(graph, regex)
    for keyword in keyword_list['verb-objects']:
        keywords = keyword.split()
        regex = verbobj_regex.format(keywords[0], keywords[1])
        found_nodes[keyword] = find_trace(graph, regex)
    for keyword in keyword_list['nouns']:
        regex = word_regex.format(keyword)
        found_nodes[keyword] = find_trace(graph, regex)
    for keyword in keyword_list['noun-objects']:
        keywords = keyword.split()
        regex = noun_phrase_regex.format(keywords[0], keywords[1])
        found_nodes[keyword] = find_trace(graph, regex)
    return found_nodes

import time
def main():
    start = time.time()
    repo_number = int(sys.argv[1])
    g = Graph(repo_number)
    trace_file = open(f"trace_links_group{repo_number}.txt", "w", encoding="utf-8") 
    req_file = open(f"data_group{repo_number}/group{repo_number}_requirements.txt", "r", encoding="utf-8")

    for line in req_file:
        token_dict = custom_extractor(line, "../keyword_extractors/SmartStopword.txt")
        trace_file.write("{}".format(line))
        trace_file.write("{}\n".format(token_dict))

        nodes = search_keyword(g, token_dict)

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