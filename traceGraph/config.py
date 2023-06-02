import os
import cv2
import socket
import sys
    
def get_mode():
    try:
        parent_mode, filter_mode, pickle_mode, filter_threshold = False, False, False, 0
        for i in range(2, len(sys.argv)):
            if sys.argv[i] == "-p":
                parent_mode = True
            elif sys.argv[i] == "-f":
                filter_mode = True
                try:
                    filter_threshold = sys.argv[i+1]
                except:
                    raise Exception("Please enter a valid filter threshold!")
            elif sys.argv[i] == "-pck":
                pickle_mode = True
            else:
                raise Exception("Please enter a valid option!")
        return parent_mode, filter_mode, pickle_mode, filter_threshold
    except:
        raise Exception("Please enter a valid mode!")

def get_search_method():

    search_method = sys.argv[1]
    if search_method != "keyword" or search_method != "word_vector":
        raise Exception("Please enter a valid search method!")
    return search_method

class Config:

    # Specify github repository
    repo_owner = 'bounswe'
    repo_number = 2
    repo_name = f'bounswe2022group{repo_number}'

    search_method = 'keyword'

    parent_mode = False
    filter_mode = False
    pickle_mode = False
    filter_threshold = 0

    neo4jConnector = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = object.__new__(cls)
            cls.instance.__initialized = False
        return cls.instance

    def __init__(self) -> None:
        if self.__initialized: return
        self.__initialized = True

        self.parent_mode, self.filter_mode, self.pickle_mode, self.filter_threshold = get_mode()
        self.search_method = get_search_method()
        self.neo4jConnector = 