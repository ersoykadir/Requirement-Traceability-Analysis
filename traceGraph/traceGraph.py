"""
Kadir Ersoy - Ecenur Sezer
Requirements Traceability Graph
"""

import requests
import json
from string import Template
import datetime
import os
from keyword_extractors.extractor_rake import extract_rake
from keyword_extractors.extractor_yake import extract_yake
from dotenv import load_dotenv
import re
load_dotenv()

username = os.getenv('GITHUB_USERNAME')
token = os.getenv('GITHUB_TOKEN')
print(username, token)

repo_owner = 'bounswe'
repo_number = 3
repo_name = f'bounswe2022group{repo_number}'

if repo_number == 2:
    issue_number_threshold = 309 # for group 2
elif repo_number == 3:
    issue_number_threshold = 258 # for group 3
else:
    raise Exception("Invalid repo number")

requirements_file_name = f'data_group{repo_number}/group{repo_number}_requirements.txt'
requirement_data_fname = f'data_group{repo_number}/requirement_data.json'
issue_data_fname = f'data_group{repo_number}/issue_data.json'
pr_data_fname = f'data_group{repo_number}/pr_data.json'
commit_data_fname = f'data_group{repo_number}/commit_data.json'
output_file = f'group{repo_number}_req_to_issue.txt'


ISSUE_queryTemplate = Template("""{
    repository(owner:"$owner", name:"$name") {
        issues(first: 100, states:CLOSED, after:$cursor) {
            totalCount
            nodes{
                url
                title
                number
                body
                createdAt 
                closedAt
                state
                milestone{
                    title
                    description
                    number
                }
                comments(first:100){
                    totalCount
                    nodes{
                        body
                    }
                }
            }
            pageInfo{
                endCursor
                hasNextPage
            }
        }
    }
}""")
PR_queryTemplate = Template("""{
    repository(owner:"$owner", name:"$name") {
        pullRequests(first:100, after:$cursor) {
            nodes{
                url
                title
                number
                body
                createdAt 
                closedAt
                state
                milestone{
                    title
                    description
                    number
                }
                comments(first:100){
                    totalCount
                    nodes{
                        body
                    }
                }
                commits(first:100){
                    totalCount
                    nodes{
                        commit{
                            oid
                            message
                            url
                            committedDate
                        }
                    }
                }
            }
            pageInfo{
                endCursor
                hasNextPage
            }
        }
    }
}""")
Commit_queryTemplate = Template("""{
    repository(owner: "$owner", name: "$name") {
        ref(qualifiedName: "master") {
            target {
                ... on Commit {
                    history(first: 100, after:$cursor) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    nodes{
                        oid
                        message
                        committedDate
                        url
                        associatedPullRequests(first:10){
                            nodes{
                                number
                            }
                        }
                        }
                    }
                }
            }
        }
    }
}""")

# Removes all the data files, helper function when data is broken or needs to be refreshed.
def clean_files():
    if os.path.exists(commit_data_fname):
        os.remove(commit_data_fname)
    if os.path.exists(issue_data_fname):
        os.remove(issue_data_fname)
    if os.path.exists(pr_data_fname):
        os.remove(pr_data_fname)
    if os.path.exists(requirement_data_fname):
        os.remove(requirement_data_fname)

issues = []
pullRequests = []
commits = []

# Acquires data from the github graphql api, given a graphql query.
def get_data_from_api(body):
    global username, token
    url = 'https://api.github.com/graphql'
    r = requests.post(url = url, json = {"query":body}, auth=(username, token))
    data = r.json()
    return data

# Gets a page of issues, appends them to the global issues list, and returns the hasNextPage and endCursor values.
def get_issue_page(body):
    global issues
    data = get_data_from_api(body)
    issues = issues + (data['data']['repository']['issues']['nodes'])
    hasNextPage = data['data']['repository']['issues']['pageInfo']['hasNextPage']
    endCursor = data['data']['repository']['issues']['pageInfo']['endCursor']
    return hasNextPage, endCursor

# Gets a page of pull requests, appends them to the global pullRequests list, and returns the hasNextPage and endCursor values.
def get_pr_page(body):
    global pullRequests
    data = get_data_from_api(body)
    pullRequests = pullRequests + (data['data']['repository']['pullRequests']['nodes'])
    hasNextPage = data['data']['repository']['pullRequests']['pageInfo']['hasNextPage']
    endCursor = data['data']['repository']['pullRequests']['pageInfo']['endCursor']
    return hasNextPage, endCursor

# Gets a page of commits, appends them to the global commits list, and returns the hasNextPage and endCursor values.
def get_commit_page(body):
    global commits
    data = get_data_from_api(body)
    commits = commits + (data['data']['repository']['ref']['target']['history']['nodes'])
    hasNextPage = data['data']['repository']['ref']['target']['history']['pageInfo']['hasNextPage']
    endCursor = data['data']['repository']['ref']['target']['history']['pageInfo']['endCursor']
    return hasNextPage, endCursor

# Gets all issues, page by page, and writes them to a json file.
def get_all_issues():
    global issues
    hasNextPage, endCursor = True, "null"
    
    # Traverse the pages
    while(hasNextPage):
        if endCursor != "null":
            endCursor = "\"" + endCursor + "\""
        # Update the query with the new endCursor
        query = ISSUE_queryTemplate.substitute(owner=repo_owner, name=repo_name, cursor=endCursor)
        # Get the next page of issues
        hasNextPage, endCursor = get_issue_page(query)
    
    # Write the issues to a json file
    f = open(issue_data_fname, 'w')
    dump = {'issues': issues}
    f.write(json.dumps(dump, indent=4))
    f.close()

# Gets all pull requests, page by page, and writes them to a json file.
def get_all_prs():
    global pullRequests
    hasNextPage, endCursor = True, "null"

    # Traverse the pages
    while(hasNextPage):
        if endCursor != "null":
            endCursor = "\"" + endCursor + "\""
        # Update the query with the new endCursor
        query = PR_queryTemplate.substitute(owner=repo_owner, name=repo_name, cursor=endCursor)
        # Get the next page of pull requests
        hasNextPage, endCursor = get_pr_page(query)

    # Write the pull requests to a json file
    f = open(pr_data_fname, 'w')
    dump = {'pullRequests': pullRequests}
    f.write(json.dumps(dump, indent=4))
    f.close()

# Gets all pull commits, page by page, and writes them to a json file.
def get_all_commits():
    global commits
    hasNextPage, endCursor = True, "null"

    # Traverse the pages
    while(hasNextPage):
        if endCursor != "null":
            endCursor = "\"" + endCursor + "\""
        # Update the query with the new endCursor
        query = Commit_queryTemplate.substitute(owner=repo_owner, name=repo_name, cursor=endCursor)
        # Get the next page of pull requests
        hasNextPage, endCursor = get_commit_page(query)

    # Write the commits to a json file
    f = open(commit_data_fname, 'w')
    dump = {'commits': commits}
    f.write(json.dumps(dump, indent=4))
    f.close()

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

def requirement_parser():

    f = open(requirements_file_name, 'r', encoding='utf-8', errors='ignore')
    data = f.readlines()
    f.close()

    requirement_nodes = {} # Dictionary of requirement nodes
    requirements = [] # List of requirement dictionaries, to be written to a json file

    for line in data:
        req = line.split(' ', 1)
        req_number = req[0]
        req_description = req[1]
        requirement_nodes[req_number] = Requirement('requirement', req_number, req_description)
        req_dict = {
            'number': req_number,
            'description': req_description
        }
        requirements.append(req_dict)
    
    # Write the requirements to a json file
    f = open(requirement_data_fname, 'w')
    dump = {'requirements': requirements}
    f.write(json.dumps(dump, indent=4))
    f.close()
    return requirement_nodes

# Parses the data from the json files and creates a dictionary of graph nodes, where the key is the issue/pr number.
def build_issue_nodes():
    global issue_number_threshold
    # Get all issues from the github api and write them to a json file.

    if not os.path.isfile(issue_data_fname): # Comment this out if the json file has broken data.
        get_all_issues()
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

# Parses the data from the json files and creates a dictionary of graph nodes, where the key is the issue/pr number.
def build_pr_nodes():
    # Get all issues from the github api and write them to a json file.
    if not os.path.isfile(pr_data_fname):# Comment this out if the json file has broken data.
        get_all_prs() 
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
def build_commit_nodes():
    # Get all issues from the github api and write them to a json file.
    if not os.path.isfile(commit_data_fname):# Comment this out if the json file has broken data.
        get_all_commits() 
    f = open(commit_data_fname, 'r')
    data = json.loads(f.read())
    f.close()
    commit_nodes = {}
    for commit in data['commits']:
        node = Commit('commit', commit['oid'], commit['message'], commit['committedDate'], commit['url'])
        commit_nodes[node.node_id] = node
    return commit_nodes

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

class Requirement(Node):
    def __init__(self, node_type, id, description):
        super().__init__(node_type, id)
        self.description = description
        self.text = self.description
        try:
            self.keywords = extract_yake(self.text)
        except Exception as e:
            print(str(e))

# Class representing the graph of software artifacts.
class Graph:
    def __init__(self):
        self.nodes = {}
        self.issue_nodes = build_issue_nodes()
        self.pr_nodes, self.commit_nodes = build_pr_nodes()
        self. commit_nodes = self.commit_nodes | build_commit_nodes()
        self.requirement_nodes = requirement_parser()

    def __str__(self):
        return f"Graph with {len(self.nodes)} nodes."

# Utility function to search for a keyword in a string.
def findWholeWord(w):
    return re.compile(r'\b{0}\b'.format(w), flags=re.IGNORECASE).search

# Search the graph for the keyword list and return the nodes that have matching keywords.
def search_keyword(keyword_list, node_id, graph):
    # Avoid the source node.
    found_nodes = {keyword: set() for keyword in keyword_list}
    for keyword in keyword_list:
        for node in graph.issue_nodes.values():
            try:
                match = findWholeWord(keyword)(node.text)
            except Exception as e:
                print(str(e))
                print(node.text)
                print(keyword)
            if match != None and node.node_id != node_id:
                found_nodes[keyword].add(node)
    
    # Print the frequency of each keyword.
    key_freq = {keyword: len(found_nodes[keyword]) for keyword in found_nodes.keys()}
    graph.requirement_nodes[node_id].freqs = key_freq
    
    result = clean_noise(found_nodes)
    return result

def clean_noise(found_nodes):
    # We have a dictionary of keywords and the nodes that contain the keyword.
    # We will clean the keywords that has a lot of false positives.
    for keyword in found_nodes.keys():
        if len(found_nodes[keyword]) > 10:
            cleaned_nodes = set()
            for node in found_nodes[keyword]: # Traverse each node
                # if the node does not contain other keywords, then it is a false positive.
                count = 0
                for key in found_nodes.keys():# other keywords
                    if key != keyword and key in node.text:
                        count += 1
                if len(found_nodes[keyword]) > 20 and count >= 2:
                    cleaned_nodes.add(node)
                elif count >= 1:
                    cleaned_nodes.add(node)
            found_nodes[keyword] = cleaned_nodes
    
    # Merge all the nodes that contain the keywords.
    result = set()
    for keyword in found_nodes.keys():
        for node in found_nodes[keyword]:
            result.add(node)
    return result

# Give each requirement to rake.py, acquiring list of keywords
# For each keyword, search the graph for the keyword and return the nodes that contain the keyword.
def req_to_issue(graph):
    for req in graph.requirement_nodes.values():
        found_nodes = search_keyword(req.keywords, req.node_id, graph)
        for node in found_nodes:
            req.traces.append(node)

#clean_files() # Clean the data when changing the target repository.
graph = Graph()
print(len(graph.issue_nodes))

req_to_issue(graph)

f = open(output_file, 'w', encoding='utf-8')
for req in graph.requirement_nodes.values():
    if len(req.traces) == 0:
        print(f"Requirement {req.node_id} has no traces.")
        continue
    print(req.traces)
    sorted_traces = sorted(req.traces, key=lambda x: x.node_id)
    print(sorted_traces)
    f.write(f"{req.node_id} {req.description}\n")
    f.write(f"{req.freqs}\n")
    for node in sorted_traces:
        f.write(f"{node.node_id} {node.title}\n")
    f.write(f"------------------------------------------------------------\n")
f.close()