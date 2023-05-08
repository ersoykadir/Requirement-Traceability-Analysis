"""
Kadir Ersoy - Ecenur Sezer
Requirements Traceability Tool

Graph and node classes for the traceability graph. 
Utilized for representing each artifact as node and finding trace links between them.
Also creates w2v model and, word vectors for each artifact.
"""

import sys
import json
import datetime
from nltk.corpus import stopwords
import string
from nltk.tokenize import word_tokenize
from gensim.models import Word2Vec as w2v
import numpy as np

sys.path.append('..')
from keyword_extractors.dependency_parsing_custom_pipeline import custom_extractor

# Utility function to convert a github timestamp to a datetime object, to calculate the time to finish an issue.
def time_to_finish(created, closed):
    closed = closed.replace('T', ' ').replace('Z', '')
    created = created.replace('T', ' ').replace('Z', '')
    closed = datetime.datetime.strptime(closed, '%Y-%m-%d %H:%M:%S')
    created = datetime.datetime.strptime(created, '%Y-%m-%d %H:%M:%S')
    time_to_finish = closed - created
    return time_to_finish

# Parses the comments of an issue or pull request.
def comment_parser(comments):
    comment_list = []
    comments = comments['nodes']
    for comment in comments:
        comment_list.append(comment['body'])
    return comment_list

# Parses the commits of a pull request.
def commit_parser(related_commits):
    commit_ids = []
    commit_nodes = {}
    related_commits = related_commits['nodes']
    for commit in related_commits:
        # Create commit object and add its id to the commit list.
        cm = commit['commit']
        commit_nodes[cm['oid']] = Commit('commit', cm['oid'], cm['message'], cm['committedDate'], cm['url'])
        commit_ids.append(cm['oid'])
    return commit_ids, commit_nodes

# Parses the data from the issue file and creates a dictionary of graph nodes, where the key is the issue number.
def build_issue_nodes(repo_number, issue_number_threshold):
    issue_data_fname = f'data_group{repo_number}/issues_data.json'
    f = open(issue_data_fname, 'r')
    data = json.loads(f.read())
    f.close()
    issue_nodes = {}
    for issue in data['issues']:
        if issue['number'] < issue_number_threshold: # Skip the issues that were created in 352.
            continue
        node = Issue('issue', issue['number'], issue['title'], issue['body'], issue['comments'], issue['state'], issue['createdAt'], issue['closedAt'], issue['url'], issue['milestone'])
        issue_nodes[node.number] = node
    return issue_nodes

# Parses the data from the pull requests file and creates a dictionary of graph nodes, where the key is the pr number.
def build_pr_nodes(repo_number):
    pr_data_fname = f'data_group{repo_number}/pullRequests_data.json'
    f = open(pr_data_fname, 'r')
    data = json.loads(f.read())
    f.close()
    pr_nodes = {}
    #commit_nodes = {}
    for pr in data['pullRequests']:
        node = PullRequest('pullRequest', pr['number'], pr['title'], pr['body'], pr['comments'], pr['state'], pr['createdAt'], pr['closedAt'], pr['url'], pr['milestone'], pr['commits'])
        pr_nodes[node.number] = node
        # Parse the commits of the pull request.
        commit_ids, related_commit_nodes = commit_parser(pr['commits'])
        node.related_commits = commit_ids
        # commit_nodes = commit_nodes | related_commit_nodes
    #return pr_nodes, commit_nodes
    return pr_nodes

# Parses the data from the commits file and creates a dictionary of graph nodes, where the key is the commit id.
def build_commit_nodes(repo_number):
    commit_data_fname = f'data_group{repo_number}/commits_data.json'
    f = open(commit_data_fname, 'r')
    data = json.loads(f.read())
    f.close()
    commit_nodes = {}
    for commit in data['commits']:
        node = Commit('commit', commit['oid'], commit['message'], commit['committedDate'], commit['url'])
        commit_nodes[node.node_id] = node
    return commit_nodes

# Parses the data from the requirements file and creates a dictionary of graph nodes, where the key is the requirement number.
def build_requirement_nodes(repo_number):
    data_fname = f'data_group{repo_number}/requirements_data.json'
    f = open(data_fname, 'r')
    data = json.loads(f.read())
    f.close()
    requirement_nodes = {}
    for req in data['requirements']:
        node = Requirement('requirement', req['number'], req['description'])
        if req['parent'] != "":
            node.parent = requirement_nodes[req['parent']]
        requirement_nodes[node.node_id] = node
    return requirement_nodes

total_missing_tokens = 0

# Class representing graph nodes. Each node represents a software artifact (issue, pull request, requirement, commit).
class Node:
    def __init__(self, node_type, node_id):
        self.node_type = node_type
        self.node_id = node_id
        self.traces = [] # List of nodes that this node traces to.	
        self.text = '' # Textual description of the node.

        # Metrics, not used now. Can be used to calculate the importance of a node etc !!
        self.number_of_connected_nodes = 0
        self.number_of_connected_commits = 0
        self.number_of_connected_requirements = 0
        self.number_of_connected_issues = 0
        self.number_of_connected_prs = 0

    # Preprocesses and tokenizes the text of the node. To be used for the word embeddings.
    def preprocess_text(self):
        self.text = self.text.rstrip('\n')
        self.text = self.text.lower()
        self.text = self.text.translate(str.maketrans('', '', string.punctuation))
        self.text = self.text.translate(str.maketrans('', '', string.digits))
        sw = stopwords.words('english')
        tokens = word_tokenize(self.text)
        self.tokens = [w for w in tokens if not w in sw]

    # Creates the word vector of the node.
    def create_vector(self, model):
        try:
            self.word_vector = []
            for token in self.tokens:
                try:
                    self.word_vector.append(model.wv[token])
                except KeyError:
                    #print(token, 'not in vocabulary')
                    global total_missing_tokens
                    total_missing_tokens += 1
            # self.word_vector = model.wv[self.tokens]
            self.average_word_vector = np.mean(self.word_vector, axis=0)
        except Exception as e:
            print(e)
            print(self.node_type, self.node_id)
            print(self.tokens)
            raise e

    def __str__(self):
        return f"Node: {self.node_type}-{self.node_id}"
    


class Issue(Node):
    def __init__(self, node_type, number, title, body, comments, state, created, closed, url, milestone):
        super().__init__(node_type, number)
        # Fields specific to issues
        self.number = number
        self.url = url
        self.title = title
        self.body = body
        self.comments = comment_parser(comments)
        self.number_of_comments = len(comments)
        self.state = state
        if closed is not None:
            self.time_to_finish = time_to_finish(created, closed)
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
    def __init__(self, node_type, id, message, committedDate, url):
        # TODO: Maybe add more info about the commit, like the files changed, additions, deletions, etc.
        # File change patches are not available in the graphQL API, so we need to use the GitHub API to get them, if necessary
        super().__init__(node_type, id)
        self.url = url
        self.message = message
        tempDate = committedDate.replace('T', ' ').replace('Z', '')
        self.committedDate = datetime.datetime.strptime(tempDate, '%Y-%m-%d %H:%M:%S')
        self.text = self.message
        self.number = id

class Requirement(Node):
    def __init__(self, node_type, id, description):
        super().__init__(node_type, id)
        self.description = description
        self.text = self.description
        self.number = id
        self.parent = None
        self.keyword_dict = {}
        # try:
        #     self.keywords = self.extract_keywords()
        # except Exception as e:
        #     print(str(e), self.node_id, self.node_type)
    def extract_keywords(self):
        try:
            print("Extracting keywords for requirement", self.node_id)
            keyword_dict = custom_extractor(self.text, '../keyword_extractors/SmartStopword.txt')
            if self.parent is not None:
                # parent_keywords = custom_extractor(self.parent.text, '../keyword_extractors/SmartStopword.txt')
                parent_keywords = self.parent.keyword_dict
                for key_type in keyword_dict:
                    keyword_dict[key_type] = list(set(keyword_dict[key_type] + parent_keywords[key_type]))
            self.keyword_dict = keyword_dict
        except Exception as e:
            print(str(e), self.node_id, self.node_type)

# Class representing the graph of software artifacts.
class Graph:
    def __init__(self, repo_number):

        if repo_number == 2:
            self.issue_number_threshold = 309 # for group 2
        elif repo_number == 3:
            self.issue_number_threshold = 258 # for group 3
        else:
            raise Exception("Invalid repo number")
        
        self.nodes = {}
        self.issue_nodes = build_issue_nodes(repo_number, self.issue_number_threshold)
        self.pr_nodes = build_pr_nodes(repo_number)
        self.commit_nodes = build_commit_nodes(repo_number)
        self.requirement_nodes = build_requirement_nodes(repo_number)
        self.nodes = self.issue_nodes | self.pr_nodes | self.commit_nodes | self.requirement_nodes
        self.artifact_nodes = self.issue_nodes | self.pr_nodes | self.commit_nodes


    def __str__(self):
        return f"Graph with {len(self.issue_nodes)} nodes."

    def create_model(self):
        texts = []
        total_tokens = 0

        # Get the tokens of each node for training the w2v model
        for node in self.nodes.values():
            node.preprocess_text()
            texts.append(node.tokens)
            total_tokens += len(node.tokens)
        
        # Train the w2v model
        self.model = w2v(
            texts,
            min_count=3,  
            sg = 1,       
            window=7      
        )
        # Create the word vectors for each node
        for node in self.nodes.values():
            node.create_vector(self.model)
        print('Total missing tokens:', total_missing_tokens)
        print('Total tokens:', total_tokens)

    # Removes the stopwords from the given token list.
    def remove_stopwords(self, tokens):
        res = []
        sw = stopwords.words('english')
        for text in tokens:
            original = text
            text = [w for w in text if w not in sw]
            if len(text) < 1:
                text = original
            res.append(text)
        return res