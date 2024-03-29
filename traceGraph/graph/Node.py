"""
Kadir Ersoy - Ecenur Sezer
Requirements Traceability Tool

Graph and node classes for the traceability graph. 
Utilized for representing each artifact as node and finding trace links between them.
Also creates w2v model and, word vectors for each artifact.
"""

from datetime import datetime
from nltk.corpus import stopwords
import string
from nltk.tokenize import word_tokenize
import numpy as np

from keyword_extractor.custom_extractor import custom_extractor
from config import Config
from nltk.stem.wordnet import WordNetLemmatizer
wnet_lemmatizer = WordNetLemmatizer()

# Class representing graph nodes. Each node represents a software artifact (issue, pull request, requirement, commit).
class Node:
    def __init__(self, node_type, number):
        self.node_type = node_type
        self.number = number
        self.text = '' # Textual description of the node.
        self.vector = None # Vector representation of the node.
        self.average_word_vector = None # Average word vector representation of the node.
        self.tokens = None # Tokens of the node.

    # Preprocesses the text of the node.
    def preprocess_text(self):
        text = self.text
        text = text.lower()
        text = text.rstrip('\n')
        text = text.translate(str.maketrans('', '', string.digits))
        sw = []
        if Config().search_method != 'keyword':
            text = text.translate(str.maketrans('', '', string.punctuation))
            sw = stopwords.words('english')

        tokens = word_tokenize(text)
        self.tokens = [wnet_lemmatizer.lemmatize(word) for word in tokens if word not in sw]
        self.text = ' '.join(self.tokens)
    
    # Creates the word vector of the node.
    def create_vector(self, model):
        try:
            word_vector = []
            total_missing_tokens = 0
            tokens = self.tokens
            if Config().parent_mode:
                if self.node_type =='requirement' and self.parent is not None:
                    tokens += self.parent.tokens
            for token in self.tokens:
                try:
                    word_vector.append(model[token])
                except KeyError:
                    #print(token, 'not in vocabulary')
                    total_missing_tokens += 1
            if len(word_vector) > 0:
                self.vector = np.mean(word_vector, axis=0)
            return total_missing_tokens
        except Exception as e:
            print(e)
            print(self.node_type, self.number)
            print(self.tokens)
            raise e
    
    # Utility function to convert a github timestamp to a datetime object, to calculate the time to finish an issue.
    def time_taken(self, created, closed):
        closed = closed.replace('T', ' ').replace('Z', '')
        created = created.replace('T', ' ').replace('Z', '')
        closed = datetime.strptime(closed, '%Y-%m-%d %H:%M:%S')
        created = datetime.strptime(created, '%Y-%m-%d %H:%M:%S')
        time_to_finish = closed - created
        return time_to_finish

    # Parses the comments of an issue or pull request.
    def comment_parser(self, comments):
        comment_list = []
        comments = comments['nodes']
        for comment in comments:
            comment_list.append(comment['body'])
        return comment_list
    def __str__(self):
        return f"Node: {self.node_type}-{self.number}"
    
class Issue(Node):
    def __init__(self, node_type, number, title, body, comments, state, created, closed, url, milestone):
        super().__init__(node_type, number)
        # Fields specific to issues
        self.number = number
        self.url = url
        self.title = title
        self.body = body
        self.comments = self.comment_parser(comments)
        self.number_of_comments = len(comments)
        self.state = state
        if closed is not None:
            self.time_to_finish = self.time_taken(created, closed)
        self.milestone = milestone
        self.text = self.title + ' ' + self.body
        # add the comments to the text
        for comment in self.comments:
            self.text += ' ' + comment

class PullRequest(Issue):
    def __init__(self, node_type, number, title, body, comments, state, created, closed, url, milestone, related_commits):
        super().__init__(node_type, number, title, body, comments, state, created, closed, url, milestone)
        self.related_commits = related_commits

class Commit(Node):
    def __init__(self, node_type, id, message, committedDate, url, associatedPullRequest):
        # TODO: Maybe add more info about the commit, like the files changed, additions, deletions, etc.
        # File change patches are not available in the graphQL API, so we need to use the GitHub API to get them, if necessary
        super().__init__(node_type, id)
        self.url = url
        self.message = message
        tempDate = committedDate.replace('T', ' ').replace('Z', '')
        self.committedDate = datetime.strptime(tempDate, '%Y-%m-%d %H:%M:%S')
        self.text = self.message
        self.associatedPullRequest = associatedPullRequest

class Requirement(Node):
    def __init__(self, node_type, number, description):
        super().__init__(node_type, number)
        self.description = description
        self.text = self.description
        self.parent = None	
        self.keyword_dict = {}
        self.traces = [] # List of nodes that this node traces to.	
        self.issue_traces = {}
        self.pr_traces = {}
        self.commit_traces = {}
    def extract_keywords(self):	
        try:	
            print("Extracting keywords for requirement", self.number)	
            keyword_dict = custom_extractor(self.text, './keyword_extractor/SmartStopword.txt', './keyword_extractor/repo_stopwords.txt')	
            if self.parent is not None and Config().parent_mode:	
                # parent_keywords = custom_extractor(self.parent.text, '../keyword_extractors/SmartStopword.txt')	
                parent_keywords = self.parent.keyword_dict	
                for key_type in keyword_dict:	
                    keyword_dict[key_type] = list(set(keyword_dict[key_type] + parent_keywords[key_type]))	
            self.keyword_dict = keyword_dict	
        except Exception as e:	
            print(str(e), self.number, self.node_type)
            raise e