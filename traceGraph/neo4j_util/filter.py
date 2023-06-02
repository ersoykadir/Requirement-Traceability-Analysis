import numpy as np

def cosine_similarity(v1, v2):
    return np.dot(v1, v2)/(np.linalg.norm(v1)*np.linalg.norm(v2))

def filter_by_similarity(node_number, trace_nodes, graph, threshold=0.01):
    filtered = {}
    a_vector = graph.nodes[node_number].vector
    # a_vector = document_embedding(graph.nodes[a])
    for traced_node_number in trace_nodes.keys():
        b_vector = graph.nodes[traced_node_number].vector
        similarity = cosine_similarity(a_vector, b_vector)

        if similarity > 0.01:
            filtered[traced_node_number] = [similarity, trace_nodes[traced_node_number][1]]

        # if node_number != traced_node_number:
        #     filtered[traced_node_number] = [similarity, trace_nodes[traced_node_number][1]]
        # else:
        #     filtered[traced_node_number] = [1, trace_nodes[traced_node_number][1]]

        # trace_nodes[traced_node_number][0] = similarity[traced_node_number]
    
    # sorted_similarity = sorted(similarity.items(), key=lambda kv: kv[1], reverse=True)
    # Return keys of sorted_similarity with values greater than 0.01
    # return [key for key, value in sorted_similarity if value > threshold]
    return filtered

def filter_traces(graph):

    for req in graph.requirement_nodes.values():
        req.issue_traces = filter_by_similarity(req.number, req.issue_traces, graph)
        req.pr_traces = filter_by_similarity(req.number, req.pr_traces, graph)
        req.commit_traces = filter_by_similarity(req.number, req.commit_traces, graph)

        # # Remove artifacts that have cosine similarity less than 0.1
        # req_to_issue[req_number] = {key: req_to_issue[req_number][key] for key in issue_similarities}
        # req_to_pr[req_number] = {key: req_to_pr[req_number][key] for key in pr_similarities}
        # req_to_commit[req_number] = {key: req_to_commit[req_number][key] for key in commit_similarities}