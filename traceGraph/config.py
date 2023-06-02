import os
import cv2
import socket
import sys
    
def get_mode():
    try:
        parent_mode, filter_mode, reset_graph, filter_threshold = False, False, False, 0
        for i in range(2, len(sys.argv)):
            if sys.argv[i] == "-p":
                parent_mode = True
            elif sys.argv[i] == "-f":
                filter_mode = True
                try:
                    filter_threshold = sys.argv[i+1]
                except:
                    raise Exception("Please enter a valid filter threshold!")
            elif sys.argv[i] == "-rg":
                reset_graph = True
            else:
                raise Exception("Please enter a valid option!")
        return parent_mode, filter_mode, reset_graph, filter_threshold
    except:
        raise Exception("Please enter a valid mode!")

def get_search_method():

    search_method = sys.argv[1]
    if search_method != "keyword" or search_method != "word_vector":
        raise Exception("Please enter a valid search method!")
    return search_method

class Config:

    # environment variables
    neo4j_username = os.environ.get('NEO4J_USERNAME')
    neo4j_password = os.environ.get('NEO4J_PASSWORD')
    neo4j_uri = os.environ.get('NEO4J_URI')
    github_username = os.environ.get('GITHUB_USERNAME')
    github_token = os.environ.get('GITHUB_TOKEN')


    # Specify github repository
    repo_owner = 'bounswe'
    repo_number = 2
    repo_name = f'bounswe2022group{repo_number}'

    # Tracing parameters
    search_method = 'keyword'
    parent_mode = False
    filter_mode = False
    reset_graph = True
    filter_threshold = 0

    filter_nodes_before_date = '2022-06-01T00:00:00Z'
    

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = object.__new__(cls)
            cls.instance.__initialized = False
        return cls.instance

    def __init__(self) -> None:
        if self.__initialized: return
        self.__initialized = True

        self.parent_mode, self.filter_mode, self.reset_graph, self.filter_threshold = get_mode()
        self.search_method = get_search_method()