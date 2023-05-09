"""
Kadir Ersoy - Ecenur Sezer
Requirements Traceability Tool

Creates traces from requirements to other artifacts using a custom keyword extractor and regex matching.
Writes traces to a file.
"""


import re, sys, time, threading
from traceGraph import Graph
sys.path.append('..')
from keyword_extractors.dependency_parsing_custom_pipeline import custom_extractor, lemmatizer, remove_stopwords_from_text


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
            # print(match, node.number)
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

# Lemmatize and remove stopwords from the artifact
def lemmatize_remove(artifact):
    artifact.text = remove_stopwords_from_text(artifact.text, "../keyword_extractors/SmartStopword.txt")
    artifact.text = lemmatizer(artifact.text)

# Lemmatize and remove stopwords from each artifact in the graph
def lemmatize_and_remove_stopwords(graph):
    threads = []
    # for art in graph.artifact_nodes.values():
    #     print(art.number)
    #     lemma_thread = threading.Thread(target=lemmatize_remove, args=(art,))
    #     threads.append(lemma_thread)
    #     lemma_thread.start()
    # for thread in threads:
    #     thread.join()
    for art in graph.artifact_nodes.values():
        lemmatize_remove(art)

def main():
    start_all = time.time()
    start = time.time()
    repo_number = int(sys.argv[1])
    g = Graph(repo_number)
    lemmatize_and_remove_stopwords(g)
    print(f"Graph created in {time.time() - start} seconds")
    trace_file = open(f"trace_links_group{repo_number}.txt", "w", encoding="utf-8") 

    for req in g.requirement_nodes.values():
        req.extract_keywords()
        token_dict = req.keyword_dict
        trace_file.write("{}".format(req.text))
        trace_file.write("{}\n".format(token_dict))

        nodes = search_keyword(g, token_dict)

        for keyword in nodes.keys():
            trace_file.write(keyword + ' ' + str(len(nodes[keyword])) + "\n")
            for node in nodes[keyword]:
                try:
                    trace_file.write(f"{node.number} {node.title}\n")
                except Exception as e:
                    print(str(e), node.number)
            trace_file.write('------------------' + '\n')
        trace_file.write('\n')
    trace_file.close()
    end = time.time()
    print(f"Time elapsed: {end - start_all}")

if __name__ == "__main__":
    main()