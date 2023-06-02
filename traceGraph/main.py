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
from neo4j_util.neo4j_connection import clean_all_data, filter_artifact
import sys

def main():
    repo_number = int(sys.argv[1])
    try:
        search_method = str(sys.argv[2])
    except:
        raise Exception("Please enter a valid search method!")
    
    parent_mode = False
    filter_mode = False
    try:
        for i in range(3, len(sys.argv)):
            if sys.argv[i] == "-f":
                filter_mode = True
            elif sys.argv[i] == "-p":
                parent_mode = True
            else:
                raise Exception("Please enter a valid option!")
        # mode = sys.argv[3]
        # if mode == "req_tree":
        #     parent_mode = True
        # else:
        #     raise Exception("Please enter a valid mode!")
    except:
        parent_mode = False
        #raise Exception("Please enter a valid mode!")
    
    # try:
    #     filter = sys.argv[4]
    #     if filter == "-f":
    #         filter_mode = True
    #     else:
    #         raise Exception("Please enter a valid option!")
    # except:
    #     filter_mode = False
    #     #raise Exception("Please enter a valid filter mode!")
    
    get_artifacts(repo_number, parent_mode)
    clean_all_data(repo_number) # Beware! This will delete all data in the neo4j database
    # TODO: There is a problem with creating only missing nodes so we have to delete all data before creation for now
    create_neo4j_nodes(repo_number)
    filter_artifact(datetime.datetime(2022,6,1).isoformat())

    if(search_method == 'word-vector'):
        trace_wv(repo_number, parent_mode) # comment above and uncomment this line to use word2vec
    elif(search_method == "keyword"):
        trace(repo_number, parent_mode, filter_mode)
    else:
        print("Please enter a valid search method!")


if __name__ == '__main__':
    main()