import numpy as np
from config import Config

def cosine_similarity(v1, v2):
    return np.dot(v1, v2)/(np.linalg.norm(v1)*np.linalg.norm(v2))

def filter_by_similarity(node_number, trace_nodes, graph):
    threshold = Config().filter_threshold
    filtered = {}
    a_vector = graph.nodes[node_number].vector
    # a_vector = document_embedding(graph.nodes[a])
    for traced_node_number in trace_nodes.keys():
        b_vector = graph.nodes[traced_node_number].vector
        similarity = cosine_similarity(a_vector, b_vector)
        if similarity > threshold:
            filtered[traced_node_number] = [similarity, trace_nodes[traced_node_number][1]]
    return filtered

def filter_traces(graph):
    print("Filtering traces by tf-idf similarity. ", "Current threshold: ", Config().filter_threshold)
    for req in graph.requirement_nodes.values():
        req.issue_traces = filter_by_similarity(req.number, req.issue_traces, graph)
        req.pr_traces = filter_by_similarity(req.number, req.pr_traces, graph)
        req.commit_traces = filter_by_similarity(req.number, req.commit_traces, graph)