"""
Kadir Ersoy - Ecenur Sezer
Requirements Traceability Graph
"""

import sys
import json
import datetime

sys.path.append('..')
from keyword_extractors.extractor_yake import extract_yake

# Utility function to convert a github timestamp to a datetime object, to calculate time to finish an issue.
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

# Parses the data from the json files and creates a dictionary of graph nodes, where the key is the issue/pr number.
def build_issue_nodes(repo_number):
    global issue_number_threshold
    # Get all issues from the github api and write them to a json file.
    issue_data_fname = f'data_group{repo_number}/issues_data.json'
    f = open(issue_data_fname, 'r')
    data = json.loads(f.read())
    f.close()
    issue_nodes = {}
    for issue in data['issues']:
        # if issue['number'] < issue_number_threshold: # Skip the issues that were created in 352.
        #     continue
        node = Issue('issue', issue['number'], issue['title'], issue['body'], issue['comments'], issue['state'], issue['createdAt'], issue['closedAt'], issue['url'], issue['milestone'])
        issue_nodes[node.number] = node
    return issue_nodes

# Parses the data from the json files and creates a dictionary of graph nodes, where the key is the issue/pr number.
def build_pr_nodes(repo_number):
    # Get all issues from the github api and write them to a json file.
    pr_data_fname = f'data_group{repo_number}/pullRequests_data.json'
    f = open(pr_data_fname, 'r')
    data = json.loads(f.read())
    f.close()
    pr_nodes = {}
    commit_nodes = {}
    for pr in data['pullRequests']:
        node = PullRequest('pullRequest', pr['number'], pr['title'], pr['body'], pr['comments'], pr['state'], pr['createdAt'], pr['closedAt'], pr['url'], pr['milestone'], pr['commits'])
        pr_nodes[node.number] = node
        # Parse the commits of the pull request.
        commit_ids, related_commit_nodes = commit_parser(pr['commits'])
        node.related_commits = commit_ids
        commit_nodes = commit_nodes | related_commit_nodes # Append the new commit nodes to the commit node dictionary.
    return pr_nodes, commit_nodes

# Parses the data from the json files and creates a dictionary of graph nodes, where the key is the commit id.
def build_commit_nodes(repo_number):
    # Get all issues from the github api and write them to a json file.
    commit_data_fname = f'data_group{repo_number}/commits_data.json'
    f = open(commit_data_fname, 'r')
    data = json.loads(f.read())
    f.close()
    commit_nodes = {}
    for commit in data['commits']:
        node = Commit('commit', commit['oid'], commit['message'], commit['committedDate'], commit['url'])
        commit_nodes[node.node_id] = node
    return commit_nodes

def build_requirement_nodes(repo_number):
    data_fname = f'data_group{repo_number}/requirements_data.json'
    f = open(data_fname, 'r')
    data = json.loads(f.read())
    f.close()
    requirement_nodes = {}
    for req in data['requirements']:
        node = Requirement('requirement', req['number'], req['description'])
        requirement_nodes[node.node_id] = node
    return requirement_nodes

# Class representing graph nodes. Each node represents a software artifact (issue, pull request, requirement, commit).
class Node:
    def __init__(self, node_type, node_id):
        self.node_type = node_type
        self.node_id = node_id
        self.traces = [] # List of nodes that this node traces to.	
        self.text = '' # Textual description of the node.
        # Metrics
        self.number_of_connected_nodes = 0
        self.number_of_connected_commits = 0
        self.number_of_connected_requirements = 0
        self.number_of_connected_issues = 0
        self.number_of_connected_prs = 0
        '''
            Some property on each node like,
            - Requirements - Vagueness, number of connected nodes
            - Issue - title, description, open/closed, **number of comments()**
            - PR - title, description, merged or not
            - Commit - commit message, code changed in that commit
        '''

    def __str__(self):
        return f"Node: {self.node_type}-{self.node_id}"
    


class Issue(Node):
    def __init__(self, node_type, number, title, body, comments, state, created, closed, url, milestone):
        super().__init__(node_type, number)
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
        try:
            self.keywords = extract_yake(self.text, '../keyword_extractors/SmartStopword.txt')
        except Exception as e:
            print(str(e))

# Class representing the graph of software artifacts.
class Graph:
    def __init__(self, repo_number):
        self.nodes = {}
        self.issue_nodes = build_issue_nodes(repo_number)
        self.pr_nodes, self.commit_nodes = build_pr_nodes(repo_number)
        self. commit_nodes = self.commit_nodes | build_commit_nodes(repo_number)
        self.requirement_nodes = build_requirement_nodes(repo_number)

    def __str__(self):
        return f"Graph with {len(self.nodes)} nodes."