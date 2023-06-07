import numpy as np
from config import Config
import math, operator

def cosine_similarity(v1, v2):
    if Config().search_method == 'tf-idf':
        return np.dot(v1, v2)
    return np.dot(v1, v2)/(np.linalg.norm(v1)*np.linalg.norm(v2))

def normalize(word_vec):
    if Config().search_method == 'tf-idf':
        return word_vec
    norm=np.linalg.norm(word_vec)
    if norm == 0: 
        return word_vec
    return word_vec/norm

def find_similar_nodes(node_number, trace_nodes, graph):
    threshold = Config().filter_threshold
    filtered = {}
    a_vector = normalize(graph.nodes[node_number].vector)
    for node in trace_nodes:
        b_vector = node.vector
        if b_vector is None:
            continue
        b_vector = normalize(b_vector)
        similarity = cosine_similarity(a_vector, b_vector)
        if similarity > 1:
            raise Exception("Similarity cannot be greater than 1")
        if similarity > threshold:
            filtered[node.number] = [similarity, [Config().search_method]]
    return filtered

def trace_w_vector(graph):
    print(f"Filtering traces by {Config().search_method} similarity. ", "Current threshold: ", Config().filter_threshold)
    for req in graph.requirement_nodes.values():
        req.issue_traces = find_similar_nodes(req.number, graph.issue_nodes.values(), graph)
        req.pr_traces = find_similar_nodes(req.number, graph.pr_nodes.values(), graph)
        req.commit_traces = find_similar_nodes(req.number, graph.commit_nodes.values(), graph)