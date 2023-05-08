"""
Kadir Ersoy - Ecenur Sezer
Requirements Traceability Tool

Creates traces from requirements to other artifacts using a custom keyword extractor and regex matching.
Writes traces to neo4j database.
"""

import sys, os, re, time, threading
from dotenv import load_dotenv
load_dotenv()
sys.path.append('..')
from keyword_extractors.dependency_parsing_custom_pipeline import custom_extractor, lemmatizer, most_frequent_words, remove_stopwords_from_text
from neo4j_connection import create_traces, neo4jConnector, create_traces_v2
from traceGraph import Graph

neo4j_password = os.getenv("NEO4J_PASSWORD")

# Regular expressions to search for keywords in text.
word_regex = r'\b{0}\b'
verbobj_regex = r'\b{0}\s((?:[\w,;:\'\"`]+\s)*){1}\b'
noun_phrase_regex = r'\b{0}\s{1}\b'

# Searches for the regex pattern in given nodes.
def search_pattern(nodes, regex, keyword, found_nodes):
    result = set()
    compiled_regex = re.compile(regex, flags=re.IGNORECASE)
    for node in nodes:
        try:
            match = compiled_regex.search(node.text)
        except Exception as e:
            print(str(e), node.number)
        if match != None:
            # result.add(node.number)
            node_number = node.number
            if node_number in found_nodes.keys():
                found_nodes[node_number].append(keyword)
            else:
                found_nodes[node_number] = [keyword]
    # result = list(result)
    #found_nodes.append((keyword, result, weight))


# # Search keyword regex pattern in given nodes and add the results to found_nodes.
# def search_pattern_multi_threaded(found_nodes, nodes, keyword, regex, weight):
#     result = search_pattern(nodes, regex)
#     found_nodes.append((keyword, result, weight))

# Given keyword list, search for each keyword in the nodes.
def search_keyword_list(nodes, keyword_list):
    found_nodes = {}
    threads = []
    for keyword in keyword_list['verbs']:
        regex = word_regex.format(keyword)
        search_thread = threading.Thread(target=search_pattern, args=(nodes, regex, keyword, found_nodes))
        threads.append(search_thread)
        search_thread.start()
    for keyword in keyword_list['verb-objects']:
        keywords = keyword.split()
        regex = verbobj_regex.format(keywords[0], keywords[1])
        search_thread = threading.Thread(target=search_pattern, args=(nodes, regex, keyword, found_nodes))
        threads.append(search_thread)
        search_thread.start()
    for keyword in keyword_list['nouns']:
        regex = word_regex.format(keyword)
        search_thread = threading.Thread(target=search_pattern, args=(nodes, regex, keyword, found_nodes))
        threads.append(search_thread)
        search_thread.start()
    for keyword in keyword_list['noun-objects']:
        keywords = keyword.split()
        regex = noun_phrase_regex.format(keywords[0], keywords[1])
        search_thread = threading.Thread(target=search_pattern, args=(nodes, regex, keyword, found_nodes))
        threads.append(search_thread)
        search_thread.start()
    
    for thread in threads:
        thread.join()
    return found_nodes

# Lemmatize and remove stopwords from the artifact
def lemmatize_remove(artifact):
    artifact.text = remove_stopwords_from_text(artifact.text, "../keyword_extractors/SmartStopword.txt")
    artifact.text = lemmatizer(artifact.text)

# Lemmatize and remove stopwords from each artifact in the graph
def lemmatize_and_remove_stopwords(graph):
    for art in graph.artifact_nodes.values():
        # print(art.node_id)
        lemmatize_remove(art)

def trace(repo_number):
    # Create graph, lemmatize and remove stopwords from each artifact
    start = time.time()
    #req_file = open(f"data_group{repo_number}/group{repo_number}_requirements.txt", "r", encoding="utf-8")
    graph = Graph(repo_number)
    lemmatize_and_remove_stopwords(graph)
    print("Time taken to lemmatize and create graph: ", time.time() - start)

    req_to_issue = {}
    req_to_pr = {}
    req_to_commit = {}

    # most frequent words
    # most_frequent_words(f"data_group{repo_number}/group{repo_number}_requirements.txt", "../keyword_extractors/SmartStopword.txt")

    # Find artifacts that have matching keywords for each requirement
    start = time.time()
    for req in graph.requirement_nodes.values():
        req_number = req.number
        req.extract_keywords()
        token_dict = req.keyword_dict

        req_to_issue[req_number] = search_keyword_list(graph.issue_nodes.values(), token_dict)
        req_to_pr[req_number] = search_keyword_list(graph.pr_nodes.values(), token_dict)
        req_to_commit[req_number] = search_keyword_list(graph.commit_nodes.values(), token_dict)

    print("Time taken to search for keywords: ", time.time() - start)

    # Connect to Neo4j and create traces
    start = time.time()
    neo = neo4jConnector("bolt://localhost:7687", "neo4j", neo4j_password)
    create_traces_v2(neo, req_to_issue, 'Issue')
    create_traces_v2(neo, req_to_pr, 'PullRequest')
    create_traces_v2(neo, req_to_commit, 'Commit')
    neo.close()
    print("Time taken to connect neo4j and create traces: ", time.time() - start)

def main():
    repo_number = int(sys.argv[1])
    trace(repo_number)

if __name__ == "__main__":
    main()