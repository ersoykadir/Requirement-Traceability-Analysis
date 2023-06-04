import re
from queue import Queue
from threading import Thread
    
# Regular expressions to search for keywords in text.
word_regex = r'\b{0}\b'
verb_dobj_regex = r'\b{0}\s+((?:[\w,;:\'\"`\/]+\s+)*){1}\b'
verb_pobj_regex = r'\b{0}\s+((?:[\w,;:\'\"`\/]+\s+)*){1}\s+((?:[\w,;:\'\"`\/]+\s+)*){2}\b'
noun_phrase_regex = r'\b{0}\s{1}\b'


# Searches for the regex pattern in given nodes.
def search_pattern(nodes, regex, keyword, weight, found_nodes):
    result = set()
    compiled_regex = re.compile(regex, flags=re.IGNORECASE)
    for node in nodes:
        try:
            match = compiled_regex.search(node.text)
        except Exception as e:
            print(str(e), node.number)
        if match != None:
            node_number = node.number
            if node_number in found_nodes.keys():
                found_nodes[node_number][0] = found_nodes[node_number][0] + weight
                found_nodes[node_number][1].append(keyword)
            else:
                found_nodes[node_number] = [weight, [keyword]]

def process_queue(q):
    while True:
        params = q.get()
        if params is None: break
        search_pattern(*params)

# Given keyword list, search for each keyword in the nodes.
def search_keyword_list(nodes, keyword_list):
    found_nodes = {} # {node_number: [weight, [keywords]]}
    q = Queue()
    process = Thread(target=process_queue, args=(q,))
    process.start()
    for keyword in keyword_list['verbs']:
        regex = word_regex.format(keyword)
        params = (nodes, regex, keyword, 0.5, found_nodes)
        q.put(params)
    for keyword in keyword_list['verb-objects']:
        keywords = keyword.split()
        if len(keywords) == 2:
            regex = verb_dobj_regex.format(keywords[0], keywords[1])
        if len(keywords) == 3:
            regex = verb_pobj_regex.format(keywords[0], keywords[1], keywords[2])
        params = (nodes, regex, keyword, 1, found_nodes)
        q.put(params)
    for keyword in keyword_list['nouns']:
        regex = word_regex.format(keyword)
        params = (nodes, regex, keyword, 0.5, found_nodes)
        q.put(params)
    for keyword in keyword_list['noun-objects']:
        keywords = keyword.split()
        regex = noun_phrase_regex.format(keywords[0], keywords[1])
        params = (nodes, regex, keyword, 1, found_nodes)
        q.put(params)
    q.put(None)
    process.join()

    return found_nodes

def keyword_search(graph):

    for req in graph.requirement_nodes.values():
        req.extract_keywords()
        token_dict = req.keyword_dict
        # Search for keywords in each artifact type
        req.issue_traces = search_keyword_list(graph.issue_nodes.values(), token_dict)
        req.pr_traces = search_keyword_list(graph.pr_nodes.values(), token_dict)
        req.commit_traces = search_keyword_list(graph.commit_nodes.values(), token_dict)
