"""
Kadir Ersoy - Ecenur Sezer
Requirements Traceability Tool

Creates traces from requirements to other artifacts using a custom keyword extractor and regex matching.
Writes traces to neo4j database.
"""

import sys, os, re, time, threading
import numpy as np
from dotenv import load_dotenv
load_dotenv()
#sys.path.append('..')

from .filter import filter_traces
from traceGraph.ground_truth import recall_and_precision
from traceGraph.graph.Graph import Graph
from traceGraph.word_vector import document_embedding

from config import Config
from neo4j_connection import neo4jConnector

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

from queue import Queue
from threading import Thread

def process_queue(q):
    while True:
        params = q.get()
        if params is None: break
        search_pattern(*params)

# Given keyword list, search for each keyword in the nodes.
def search_keyword_list(nodes, keyword_list):
    found_nodes = {} # {node_number: [weight, [keywords]]}
    
    threads = []
    q = Queue()
    process = Thread(target=process_queue, args=(q,))
    process.start()
    for keyword in keyword_list['verbs']:
        regex = word_regex.format(keyword)
        params = (nodes, regex, keyword, 0.5, found_nodes)
        q.put(params)
        # search_thread = threading.Thread(target=search_pattern, args=(nodes, regex, keyword, 0.5, found_nodes))
        # threads.append(search_thread)
        # search_thread.start()
    for keyword in keyword_list['verb-objects']:
        keywords = keyword.split()
        if len(keywords) == 2:
            regex = verb_dobj_regex.format(keywords[0], keywords[1])
        if len(keywords) == 3:
            regex = verb_pobj_regex.format(keywords[0], keywords[1], keywords[2])
        params = (nodes, regex, keyword, 1, found_nodes)
        q.put(params)
        # search_thread = threading.Thread(target=search_pattern, args=(nodes, regex, keyword, 1, found_nodes))
        # threads.append(search_thread)
        # search_thread.start()
    for keyword in keyword_list['nouns']:
        regex = word_regex.format(keyword)
        params = (nodes, regex, keyword, 0.5, found_nodes)
        q.put(params)
        # search_thread = threading.Thread(target=search_pattern, args=(nodes, regex, keyword, 0.5, found_nodes))
        # threads.append(search_thread)
        # search_thread.start()
    for keyword in keyword_list['noun-objects']:
        keywords = keyword.split()
        regex = noun_phrase_regex.format(keywords[0], keywords[1])
        params = (nodes, regex, keyword, 1, found_nodes)
        q.put(params)
        # search_thread = threading.Thread(target=search_pattern, args=(nodes, regex, keyword, 1, found_nodes))
        # threads.append(search_thread)
        # search_thread.start()
    q.put(None)
    process.join()

    # for thread in threads:
    #     thread.join()
    
    # for node_number in found_nodes.keys():
    #     try:
    #         found_nodes[node_number] = [found_nodes[node_number][0], list(set(found_nodes[node_number][1]))]
    #     except Exception as e:
    #         print(str(e), node_number, found_nodes[node_number])
    #         raise e
    return found_nodes

def combine_results(graph):
    req_to_issue = {}
    req_to_pr = {}
    req_to_commit = {}
    for req in graph.requirement_nodes.values():
        req_number = req.number
        req_to_issue[req_number] = req.issue_traces
        req_to_pr[req_number] = req.pr_traces
        req_to_commit[req_number] = req.commit_traces
    return req_to_issue, req_to_pr, req_to_commit

def trace_dict_to_list(req_to_issue, req_to_pr, req_to_commit):
    
    issue_traces = [[r_num, trace] for r_num, trace in zip(req_to_issue.keys(), req_to_issue.values())]
    pr_traces = [[r_num, trace] for r_num, trace in zip(req_to_pr.keys(), req_to_pr.values())]
    commit_traces = [[r_num, trace] for r_num, trace in zip(req_to_commit.keys(), req_to_commit.values())]
    return issue_traces, pr_traces, commit_traces


import pickle
def trace():
    # Create graph, lemmatize and remove stopwords from each artifact
    start = time.time()
    if os.path.exists(f"data_{Config().repo_name}/graph.pkl") and not Config().reset_graph:
        graph = pickle.load(open(f"data_{Config().repo_name}/graph.pkl", "rb"))
    else:
        graph = Graph()
    print("Time taken to lemmatize and create graph: ", time.time() - start)

    # Create tfidf model
    graph.create_model('tfidf')

    # Find artifacts that have matching keywords for each requirement
    start = time.time()
    for req in graph.requirement_nodes.values():
        req_number = req.number
        req.extract_keywords()
        token_dict = req.keyword_dict

        # Search for keywords in each artifact type
        req.issue_traces = search_keyword_list(graph.issue_nodes.values(), token_dict)
        req.pr_traces = search_keyword_list(graph.pr_nodes.values(), token_dict)
        req.commit_traces = search_keyword_list(graph.commit_nodes.values(), token_dict)
        # print(req.commit_traces)
        #req_to_issue[req_number] = search_keyword_list(graph.issue_nodes.values(), token_dict)
        #req_to_pr[req_number] = search_keyword_list(graph.pr_nodes.values(), token_dict)
        #req_to_commit[req_number] = search_keyword_list(graph.commit_nodes.values(), token_dict)

    print("Time taken to search for keywords: ", time.time() - start)

    graph.connect_prs_from_commits()

    # Filter by similarity
    if Config().filter_mode:
        start = time.time()
        filter_traces(graph)
        print("Time taken to filter traces: ", time.time() - start)

   # Combine results
    req_to_issue, req_to_pr, req_to_commit = combine_results(graph)

    # Recall and precision
    recall_and_precision(graph)

    # Connect to Neo4j and create traces
    start = time.time()
    issue_traces, pr_traces, commit_traces = trace_dict_to_list(req_to_issue, req_to_pr, req_to_commit)
    neo4jConnector().create_traces_v3(issue_traces, 'Issue')
    neo4jConnector().create_traces_v3(pr_traces, 'PullRequest')
    neo4jConnector().create_traces_v3(commit_traces, 'Commit')
    neo4jConnector().link_commits_prs()
    neo4jConnector().close()
    print("Time taken to connect neo4j and create traces: ", time.time() - start)