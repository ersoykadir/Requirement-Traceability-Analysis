from artifacts import get_artifacts
from neo4j_parser import create_neo4j_nodes
from neo4j_trace import trace
from neo4j_trace_wv import trace as trace_wv
from neo4j_connection import clean_all_data
import sys

def main():
    repo_number = int(sys.argv[1])
    get_artifacts(repo_number)
    clean_all_data(repo_number) # Beware! This will delete all data in the neo4j database
    # TODO: There is a problem with creating only missing nodes so we have to delete all data before creation for now
    create_neo4j_nodes(repo_number)
    trace(repo_number)
    # trace_wv(repo_number) # comment above and uncomment this line to use word2vec

if __name__ == '__main__':
    main()