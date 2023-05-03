import sys
import re
import time
from traceGraph import Graph
sys.path.append('..')
from keyword_extractors.dependency_parsing_custom_pipeline import custom_extractor, lemmatizer, most_frequent_words, remove_stopwords_from_text
from neo4j_connection import create_traces, neo4jConnector, neo4j_password, create_traces_w2v
import threading

word_regex = r'\b{0}\b'
verbobj_regex = r'\b{0}\s((?:[\w,;:\'\"`]+\s)*){1}\b'
noun_phrase_regex = r'\b{0}\s{1}\b'

# def regex_match(issue, compiled_regex, found_nodes):
#     try:
#         match = compiled_regex.search(issue.text)
#     except Exception as e:
#         print(str(e))
#         print(issue.number)
#     if match != None:
#         # print(match, node.node_id)
#         found_nodes.add(issue.number)

# def search_keyword_multi_threaded(nodes, regex):
#     start = time.time()
#     found_nodes = set()
#     compiled_regex = re.compile(regex, flags=re.IGNORECASE)
#     threads = []
#     for issue in nodes:
#         t = threading.Thread(target=regex_match, args=(issue, compiled_regex, found_nodes))
#         threads.append(t)
#         t.start()
#     # Maybe not wait?
#     for thread in threads:
#         thread.join()
#     end = time.time()
#     #print("Time taken to search for keyword: ", end - start)
#     return list(found_nodes)

def search_keyword(nodes, regex):
    found_nodes = set()
    compiled_regex = re.compile(regex, flags=re.IGNORECASE)
    for issue in nodes:
        try:
            match = compiled_regex.search(issue.text)
            # if issue.number == 415:
            #     print(issue.text)
            #     print(regex)
            #     print(match)
        except Exception as e:
            print(str(e))
            print(issue.number)
        if match != None:
            # print(match, node.node_id)
            found_nodes.add(issue.number)
    return list(found_nodes)

def search_keyword_multi_threaded(found_nodes, nodes, keyword, regex):
    result = search_keyword(nodes, regex)
    found_nodes.append((keyword, result, 0.5))

def search_keyword_list(nodes, keyword_list):
    found_nodes = []
    threads = []
    for keyword in keyword_list['verbs']:
        # result = search_keyword(nodes, word_regex.format(keyword))
        # found_nodes.append((keyword, result, 0.5))
        search_thread = threading.Thread(target=search_keyword_multi_threaded, args=(found_nodes, nodes, keyword, word_regex.format(keyword)))
        threads.append(search_thread)
        search_thread.start()
    for keyword in keyword_list['verb-objects']:
        keywords = keyword.split()
        regex = verbobj_regex.format(keywords[0], keywords[1])
        # result = search_keyword(nodes, regex)
        # found_nodes.append((keyword, result, 1))
        search_thread = threading.Thread(target=search_keyword_multi_threaded, args=(found_nodes, nodes, keyword, regex))
        threads.append(search_thread)
        search_thread.start()
    for keyword in keyword_list['nouns']:
        # result = search_keyword(nodes, word_regex.format(keyword))
        # found_nodes.append((keyword, result, 0.5))
        search_thread = threading.Thread(target=search_keyword_multi_threaded, args=(found_nodes, nodes, keyword, word_regex.format(keyword)))
        threads.append(search_thread)
        search_thread.start()
    for keyword in keyword_list['noun-objects']:
        keywords = keyword.split()
        regex = noun_phrase_regex.format(keywords[0], keywords[1])
        # result = search_keyword(nodes, noun_phrase_regex.format(keywords[0], keywords[1]))
        # found_nodes.append((keyword, result, 1))
        search_thread = threading.Thread(target=search_keyword_multi_threaded, args=(found_nodes, nodes, keyword, regex))
        threads.append(search_thread)
        search_thread.start()
    for thread in threads:
        thread.join()
    return found_nodes

def lemmatize_issue(issue):
    issue.text = remove_stopwords_from_text(issue.text, "../keyword_extractors/SmartStopword.txt")
    issue.text = lemmatizer(issue.text)

def lemmatize_and_remove_stopwords(graph):
    threads = []
    for issue in graph.issue_nodes.values():
        # issue.text = remove_stopwords_from_text(issue.text, "../keyword_extractors/SmartStopword.txt")
        # issue.text = lemmatizer(issue.text)
        lemma_thread = threading.Thread(target=lemmatize_issue, args=(issue,))
        threads.append(lemma_thread)
        lemma_thread.start()
    for thread in threads:
        thread.join()

def trace(repo_number):
    req_file = open(f"data_group{repo_number}/group{repo_number}_requirements.txt", "r", encoding="utf-8")
    start = time.time()
    graph = Graph(repo_number)
    lemmatize_and_remove_stopwords(graph)
    print("Time taken to lemmatize and create graph: ", time.time() - start)
    req_to_issue = {}
    req_to_pr = {}
    req_to_commit = {}

    # most frequent words
    # most_frequent_words(f"data_group{repo_number}/group{repo_number}_requirements.txt", "../keyword_extractors/SmartStopword.txt")

    start = time.time()
    for line in req_file:
        line = line.split(' ', 1)
        req_number, description = line[0], line[1]
        token_dict = custom_extractor(description, "../keyword_extractors/SmartStopword.txt")

        req_to_issue[req_number] = search_keyword_list(graph.issue_nodes.values(), token_dict)
        req_to_pr[req_number] = search_keyword_list(graph.pr_nodes.values(), token_dict)
        req_to_commit[req_number] = search_keyword_list(graph.commit_nodes.values(), token_dict)
    end = time.time()
    print("Time taken to search for keywords: ", end - start)
    start = time.time()
    # Connect to Neo4j and create traces
    neo = neo4jConnector("bolt://localhost:7687", "neo4j", neo4j_password)
    create_traces(neo, req_to_issue, 'Issue')
    create_traces(neo, req_to_pr, 'PullRequest')
    create_traces(neo, req_to_commit, 'Commit')
    neo.close()
    end = time.time()
    print("Time taken to connect neo4j and create traces: ", end - start)

import math, operator

def dot_product(v1, v2):
    return sum(map(operator.mul, v1, v2))

def cos_sim(v1, v2):
    prod = dot_product(v1, v2)
    len1 = math.sqrt(dot_product(v1, v1))
    len2 = math.sqrt(dot_product(v2, v2))
    return prod / (len1 * len2)

def find_similar_nodes(artifact_nodes, req_node, type, topn=10):
    # This currently connects best 10 nodes for each artifact type
    # Making it homogenous is not a good idea
    # We can connect best 20-30 nodes for any artifact type
    try:
        similarities = []
        for artifact in artifact_nodes:
            try:
                if math.isnan(artifact.average_word_vector):
                    continue
            except:
                pass
            similarity = cos_sim(req_node.average_word_vector, artifact.average_word_vector)
            similarities.append((artifact, similarity))
        similarities.sort(key=lambda x: x[1], reverse=True)
        similar_nodes = []
        for i in range(topn):
            similar_nodes.append(similarities[i][0].node_id) # we might want to return the similarity score as well
        return similar_nodes
    except Exception as e:
        print(str(e))
import numpy as np
def trace_word2vec(repo_number):

    req_file = open(f"data_group{repo_number}/group{repo_number}_requirements.txt", "r", encoding="utf-8")
    start = time.time()
    graph = Graph(repo_number)
    graph.create_model()
    print("Time taken to create graph and word2vec model: ", time.time() - start)
    req_to_issue = {}
    req_to_pr = {}
    req_to_commit = {}

    start = time.time()
    for line in req_file:
        line = line.split(' ', 1)
        req_number, description = line[0], line[1]

        req_to_issue[req_number] = find_similar_nodes(graph.issue_nodes.values(), graph.requirement_nodes[req_number], 'Issue')
        req_to_pr[req_number] = find_similar_nodes(graph.pr_nodes.values(), graph.requirement_nodes[req_number], 'PullRequest')
        req_to_commit[req_number] = find_similar_nodes(graph.commit_nodes.values(), graph.requirement_nodes[req_number], 'Commit')
    end = time.time()
    print("Time taken to search for similar nodes: ", end - start)
    print(req_to_issue)
    print(req_to_pr)
    print(req_to_commit)
    start = time.time()
    # Connect to Neo4j and create traces
    neo = neo4jConnector("bolt://localhost:7687", "neo4j", neo4j_password)
    create_traces_w2v(neo, req_to_issue, 'Issue')
    create_traces_w2v(neo, req_to_pr, 'PullRequest')
    create_traces_w2v(neo, req_to_commit, 'Commit')
    neo.close()
    end = time.time()
    print("Time taken to connect neo4j and create traces: ", end - start)

def main():
    repo_number = int(sys.argv[1])
    trace(repo_number)

if __name__ == "__main__":
    main()