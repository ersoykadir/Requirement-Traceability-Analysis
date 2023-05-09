"""
Kadir Ersoy - Ecenur Sezer
Requirements Traceability Tool

How to run:     python ./main.py <repo_number> <search_method>
Please beware that neo4j server should be up before running this script. Further details can be found in ReadME.
"""

import datetime
from artifacts import get_artifacts
from neo4j_parser import create_neo4j_nodes
from neo4j_trace import trace
from neo4j_trace_wv import trace as trace_wv
from neo4j_connection import clean_all_data, filter_artifact
import sys

def main():
    repo_number = int(sys.argv[1])
    try:
        search_method = str(sys.argv[2])
    except:
        raise Exception("Please enter a valid search method!")
    get_artifacts(repo_number)
    clean_all_data(repo_number) # Beware! This will delete all data in the neo4j database
    # TODO: There is a problem with creating only missing nodes so we have to delete all data before creation for now
    create_neo4j_nodes(repo_number)
    filter_artifact(datetime.datetime(2022,6,1).isoformat())

    if(search_method == 'word-vector'):
        trace_wv(repo_number) # comment above and uncomment this line to use word2vec
    elif(search_method == "keyword"):
        trace(repo_number)
    else:
        print("Please enter a valid search method!")


if __name__ == '__main__':
    main()