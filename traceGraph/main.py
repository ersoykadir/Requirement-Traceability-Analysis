"""
Kadir Ersoy - Ecenur Sezer
Requirements Traceability Tool

How to run:     python ./main.py <search_method> <options>
Please beware that neo4j server should be up before running this script. Further details can be found in ReadME.
<search_method>:   keyword, tf-idf, word-vector
<options>:         -rt, -rg
-rt:    requirement tree mode,
        includes parent requirements for keyword extraction, requires a file named 'requirements(req_tree).txt' in the data directory
-rg:    reset graph,
        deletes the graph pickle to re-create the graph from scratch
"""

from artifacts.artifacts import get_artifacts
from trace_util.neo4j_parser import create_neo4j_nodes
from trace_util.trace import trace
from trace_util.neo4j_connection import neo4jConnector

from config import Config

def main():
    
    # Get software development artifacts and requirements
    get_artifacts()

    # Create neo4j nodes
    neo4jConnector().clean_all_data() 
    create_neo4j_nodes()
    # Filters artifacts before a given date, if specified in config.py
    # This was specific for the student projects that we used for testing, comment out if not needed
    neo4jConnector().filter_artifacts(Config().filter_nodes_before_date)

    # Find trace links
    trace()

if __name__ == '__main__':
    main()