"""
Kadir Ersoy - Ecenur Sezer
Requirements Traceability Tool

Creates traces from requirements to other artifacts using word vectors and cosine similarity.
Writes traces to neo4j database.
"""

import time, os, sys, math, operator
from neo4j_connection import neo4jConnector, create_traces_w2v
from traceGraph import Graph
from dotenv import load_dotenv
load_dotenv()

neo4j_password = os.getenv('NEO4J_PASSWORD')

def dot_product(v1, v2):
    return sum(map(operator.mul, v1, v2))

def cos_sim(v1, v2):
    prod = dot_product(v1, v2)
    len1 = math.sqrt(dot_product(v1, v1))
    len2 = math.sqrt(dot_product(v2, v2))
    return prod / (len1 * len2)

def find_similar_nodes(artifact_nodes, req_node, topn=20):
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

def trace(repo_number):

    # Create graph and word2vec model
    # Graph is created from the given github data
    # It is used to find similar artifacts for each requirement
    start = time.time()
    req_file = open(f"data_group{repo_number}/group{repo_number}_requirements.txt", "r", encoding="utf-8")
    graph = Graph(repo_number)
    graph.create_model()
    print("Time taken to create graph and word2vec model: ", time.time() - start)

    req_to_issue = {}
    req_to_pr = {}
    req_to_commit = {}

    # Find artifacts similar to each requirement
    start = time.time()
    for line in req_file:
        line = line.split(' ', 1)
        req_number = line[0]
        requirement = graph.requirement_nodes[req_number]

        req_to_issue[req_number] = find_similar_nodes(graph.issue_nodes.values(), requirement)
        req_to_pr[req_number] = find_similar_nodes(graph.pr_nodes.values(), requirement)
        req_to_commit[req_number] = find_similar_nodes(graph.commit_nodes.values(), requirement)
    
    print("Time taken to search for similar nodes: ", time.time() - start)

    # Connect to Neo4j and create traces
    start = time.time()
    neo = neo4jConnector("bolt://localhost:7687", "neo4j", neo4j_password)
    create_traces_w2v(neo, req_to_issue, 'Issue')
    create_traces_w2v(neo, req_to_pr, 'PullRequest')
    create_traces_w2v(neo, req_to_commit, 'Commit')
    neo.close()
    print("Time taken to connect neo4j and create traces: ", time.time() - start)

def main():
    repo_number = int(sys.argv[1])
    trace(repo_number)

if __name__ == '__main__':
    main()