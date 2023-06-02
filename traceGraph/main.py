"""
Kadir Ersoy - Ecenur Sezer
Requirements Traceability Tool

How to run:     python ./main.py <repo_number> <search_method>
Please beware that neo4j server should be up before running this script. Further details can be found in ReadME.
"""

import datetime
from artifacts.artifacts import get_artifacts
from neo4j_util.neo4j_parser import create_neo4j_nodes
from neo4j_util.neo4j_trace import trace
from neo4j_util.neo4j_trace_wv import trace as trace_wv
from neo4j_util.neo4j_connection import clean_all_data, filter_artifacts

from config import Config

def main():
    
    get_artifacts()
    clean_all_data() # Beware! This will delete all data in the neo4j database
    create_neo4j_nodes()
    filter_artifacts(datetime.datetime(2022,6,1).isoformat())

    if(search_method == 'word-vector'):
        trace_wv(repo_number, parent_mode) # comment above and uncomment this line to use word2vec
    elif(search_method == "keyword"):
        trace(repo_number, parent_mode, filter_mode)
    else:
        print("Please enter a valid search method!")

    


if __name__ == '__main__':
    main()