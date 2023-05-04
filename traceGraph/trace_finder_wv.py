"""
Kadir Ersoy - Ecenur Sezer
Requirements Traceability Tool

Creates traces from requirements to other artifacts using word vectors and cosine similarity.
Writes traces to a file.
"""

from traceGraph import Graph
import sys
sys.path.append('..')
from keyword_extractors.dependency_parsing_custom_pipeline import custom_extractor

import math, operator

def dot_product(v1, v2):
    return sum(map(operator.mul, v1, v2))

def cos_sim(v1, v2):
    prod = dot_product(v1, v2)
    len1 = math.sqrt(dot_product(v1, v1))
    len2 = math.sqrt(dot_product(v2, v2))
    return prod / (len1 * len2)

def find_similar_issues(graph, req_number, topn=10):
    try:
        node = graph.requirement_nodes[req_number]
        similarities = []
        for issue in graph.issue_nodes.values():
            similarity = cos_sim(node.average_word_vector, issue.average_word_vector)
            similarities.append((issue, similarity))
        similarities.sort(key=lambda x: x[1], reverse=True)
        similar_nodes = []
        for i in range(topn):
            similar_nodes.append((similarities[i][0].node_id, similarities[i][0].title, similarities[i][1]))
    except Exception as e:
        print(str(e))
        return []
    return similar_nodes

def main():
    repo_number = int(sys.argv[1])
    trace_file = open(f"wordvector_trace_links_group{repo_number}.txt", "w", encoding="utf-8") 
    req_file = open(f"data_group{repo_number}/group{repo_number}_requirements.txt", "r", encoding="utf-8")

    g = Graph(repo_number)
    g.create_model() # Creating word2vec model and vectorizing nodes

    for line in req_file:
        trace_file.write("{}".format(line))
        line = line.split(' ', 1)
        req_number = line[0]
        result = find_similar_issues(g, req_number)
        for issue in result:
            trace_file.write("{} {} - sim:  {}\n".format(issue[0], issue[1], issue[2]))
        trace_file.write("\n")
    trace_file.close()
    req_file.close()

if __name__ == "__main__":
    main()