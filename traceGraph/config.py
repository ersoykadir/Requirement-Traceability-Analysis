import os
import sys

# Provide a how to run error message 
how_to_run = f"\nHow to Run:   python main.py <search_method> <options> \n"
options_description = f"""Options:  -rt, -rg
-rt:    requirement tree mode, 
        includes parent requirements for keyword extraction, requires a file named 'requirements.txt' in the root directory of the repository
-rg:    reset graph,
        deletes the graph pickle to re-create the graph from scratch
"""
how_to_run += options_description
    
def get_mode():
    global how_to_run
    try:
        parent_mode = False
        reset_graph = False
        for i in range(2, len(sys.argv)):
            if sys.argv[i] == "-rt":
                parent_mode = True
            elif sys.argv[i] == "-rg":
                reset_graph = True
            else:
                raise Exception("Please enter a valid option!")
        return parent_mode, reset_graph
    except Exception as e:
        print("Please enter a valid option!", str(e) + "\n" )
        raise ValueError(how_to_run) from None

def get_search_method(possible_search_methods):
    global how_to_run
    try:
        search_method = sys.argv[1]
        if search_method not in possible_search_methods: 
            raise Exception()
        return search_method
    except Exception as e:
        print("Please enter a valid search method!", str(e) + "\n")
        p = "Possible search methods: " + str(possible_search_methods)
        raise ValueError(p + how_to_run) from None

class Config:

    # environment variables
    neo4j_username = os.environ.get('NEO4J_USERNAME')
    neo4j_password = os.environ.get('NEO4J_PASSWORD')
    neo4j_uri = os.environ.get('NEO4J_URI')
    github_username = os.environ.get('GITHUB_USERNAME')
    github_token = os.environ.get('GITHUB_TOKEN')


    # Specify github repository
    repo = 'bounswe/bounswe2022group2'
    repo_owner, repo_name = repo.split('/')

    # Tracing parameters
    possible_search_methods = ['keyword', 'tf-idf', 'word-vector']
    search_method = 'keyword'
    parent_mode = False
    reset_graph = False
    experiment_mode = False
    filter_threshold = 0.65

    pretrained_model_path = r"C:\Users\KadirERSOY\gensim-data\word2vec-google-news-300\GoogleNews-vectors-negative300.bin"

    filter_nodes_before_date = '2022-06-01'
    

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = object.__new__(cls)
            cls.instance.__initialized = False
        return cls.instance

    def __init__(self) -> None:
        if self.__initialized: return
        self.__initialized = True
        
        if len(sys.argv) > 1:
            self.search_method = get_search_method(self.possible_search_methods)
            self.parent_mode, self.reset_graph = get_mode()
