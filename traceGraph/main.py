"""
Kadir Ersoy - Ecenur Sezer
Requirements Traceability Tool

How to run:     python ./main.py <repo_number> <search_method>
Please beware that neo4j server should be up before running this script. Further details can be found in ReadME.
"""

from artifacts.artifacts import get_artifacts
from neo4j_util.neo4j_parser import create_neo4j_nodes
from neo4j_util.neo4j_trace import trace
from neo4j_util.neo4j_trace_wv import trace as trace_wv
from neo4j_util.neo4j_connection import neo4jConnector

from config import Config

def main():
    
    get_artifacts()
    neo4jConnector().clean_all_data() # Beware! This will delete all data in the neo4j database
    create_neo4j_nodes()
    neo4jConnector().filter_artifacts(Config().filter_nodes_before_date[:10])

    if(Config().search_method == 'word-vector'):
        trace_wv() # comment above and uncomment this line to use word2vec
    elif(Config().search_method == "keyword"):
        trace()
    else:
        print("Please enter a valid search method!")

    


if __name__ == '__main__':
    main()