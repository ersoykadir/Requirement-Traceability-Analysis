"""
Requirements Traceability Tool

Creates traces from requirements to other artifacts using a custom keyword extractor and regex matching.
Writes traces to neo4j database.
"""

import os, time

from ground_truth import recall_and_precision
from graph.Graph import Graph

from config import Config
from trace_util.neo4j_connection import neo4jConnector


"""
    Gather all foundd trace links to send to the neo4j database easily.
"""
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

"""
    Convert trace dictionary to list to send to neo4j database.
"""
def trace_dict_to_list(trace_dict):
    trace_list = []
    for r_num, traces in zip(trace_dict.keys(), trace_dict.values()):
        artifacts = list(traces.keys())
        trace = list(traces.values())
        pairs = [[i, j] for i, j in zip(artifacts, trace)]
        trace_list.append([r_num, pairs])

    return trace_list

from trace_util.keyword_search import keyword_search
from .vector_trace import trace_w_vector
"""
    Find trace links using the specified search method.
"""
def find_traces(graph):
    if Config().search_method == 'keyword':
        keyword_search(graph)
    elif Config().search_method == 'tf-idf':
        # graph.create_model('tf-idf')
        trace_w_vector(graph)
    elif Config().search_method == 'word-vector':
        # graph.create_model('word-vector')
        trace_w_vector(graph)
    elif Config().search_method == 'llm-vector':
        # graph.create_model('llm-vector')
        trace_w_vector(graph)

import pickle
"""
    Create traces from requirements to other artifacts and write to neo4j database.
"""
def trace(graph=None):
    # Create graph for easy access to nodes
    # If graph is already created, load it from pickle
    # TODO: This graph can be loaded from neo4j database instead of pickle or json
    start = time.time()
    if Config().experiment_mode and graph is not None:
        print("Graph is already created.")
    else:
        if os.path.exists(f"data_{Config().repo_name}/graph.pkl") and not Config().reset_graph:
            graph = pickle.load(open(f"data_{Config().repo_name}/graph.pkl", "rb"))
        else:
            graph = Graph()
        print("Time taken to create graph: ", time.time() - start)

    # Find artifacts that have matching keywords for each requirement
    start = time.time()
    find_traces(graph)
    print("Time taken to search for keywords: ", time.time() - start)

    # Connect commit trace links over their related pull requests if they have one
    # This simplifies the graph and makes it easier to trace
    graph.connect_prs_from_commits()

    # Gather trace links for each requirement to send to the neo4j database easily
    req_to_issue, req_to_pr, req_to_commit = combine_results(graph)

    # Connect to Neo4j and create traces
    start = time.time()
    if Config().experiment_mode:
        # Recall and precision
        recall_and_precision(graph)
    else:
        # Convert trace dictionaries to lists
        issue_traces = trace_dict_to_list(req_to_issue)
        pr_traces = trace_dict_to_list(req_to_pr)
        commit_traces = trace_dict_to_list(req_to_commit)
        # Create traces in neo4j database
        neo4jConnector().create_traces_v3(issue_traces, 'Issue')
        neo4jConnector().create_traces_v3(pr_traces, 'PullRequest')
        neo4jConnector().create_traces_v3(commit_traces, 'Commit')
        neo4jConnector().link_commits_prs() # Link commits to their related pull requests
        neo4jConnector().close()
    print("Time taken to connect neo4j and create traces: ", time.time() - start)