import sys
import re
import time
from traceGraph import Graph
sys.path.append('..')
from keyword_extractors.dependency_parsing_custom_pipeline import custom_extractor, lemmatizer, most_frequent_words, remove_stopwords_from_text
from neo4j_connection import create_req_issue_traces
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
        except Exception as e:
            print(str(e))
            print(issue.number)
        if match != None:
            # print(match, node.node_id)
            found_nodes.add(issue.number)
    return list(found_nodes)

def search_keyword_list(nodes, keyword_list):
    found_nodes = []
    for keyword in keyword_list['verbs']:
        result = search_keyword(nodes, word_regex.format(keyword))
        found_nodes.append((keyword, result, 0.5))
    for keyword in keyword_list['verb-objects']:
        keywords = keyword.split()
        result = search_keyword(nodes, verbobj_regex.format(keywords[0], keywords[1]))
        found_nodes.append((keyword, result, 1))
    for keyword in keyword_list['nouns']:
        result = search_keyword(nodes, word_regex.format(keyword))
        found_nodes.append((keyword, result, 0.5))
    for keyword in keyword_list['noun-objects']:
        keywords = keyword.split()
        result = search_keyword(nodes, noun_phrase_regex.format(keywords[0], keywords[1]))
        found_nodes.append((keyword, result, 1))
    return found_nodes

def lemmatize_issue(issue):
    issue.text = lemmatizer(issue.text)

def lemmatize_and_remove_stopwords(graph):
    start = time.time()
    threads = []
    for issue in graph.issue_nodes.values():
        issue.text = lemmatizer(issue.text)
        issue.text = remove_stopwords_from_text(issue.text, "../keyword_extractors/SmartStopword.txt")
        # lemma_thread = threading.Thread(target=lemmatize_issue, args=(issue,))
        # threads.append(lemma_thread)
        # lemma_thread.start()
    # for thread in threads:
    #     thread.join()
    end = time.time()
    print("Time taken to lemmatize all graph: ", end - start)

def trace(repo_number):
    req_file = open(f"data_group{repo_number}/group{repo_number}_requirements.txt", "r", encoding="utf-8")
    start = time.time()
    graph = Graph(repo_number)
    lemmatize_and_remove_stopwords(graph)
    print("Time taken to create graph: ", time.time() - start)
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

    # Connect to Neo4j and create traces
    create_req_issue_traces(req_to_issue, 'Issue')
    create_req_issue_traces(req_to_pr, 'PullRequest')
    create_req_issue_traces(req_to_commit, 'Commit')
    end = time.time()
    print("Time taken to create traces: ", end - start)

def main():
    repo_number = sys.argv[1]
    trace(repo_number)

if __name__ == "__main__":
    main()