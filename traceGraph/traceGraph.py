"""
Kadir Ersoy - Ecenur Sezer
Requirements Traceability Graph
"""

import requests
import json
from string import Template
import datetime
import os

repo_owner = 'bounswe'
repo_name = 'bounswe2022group2'

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
        pullRequests(first:100,states:MERGED, after:$cursor) {
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

issues = []
pullRequests = []
commits = []

# Acquires data from the github graphql api, given a graphql query.
def get_data_from_api(body):
    url = 'https://api.github.com/graphql'
    username = 'ersoykadir'
    token = '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'
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
    f = open('issue_data.json', 'w')
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
    f = open('pr_data.json', 'w')
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
    f = open('commit_data.json', 'w')
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

# Parses the data from the json files and creates a dictionary of graph nodes, where the key is the issue/pr number.
def build_issue_nodes():
    # Get all issues from the github api and write them to a json file.
    if not os.path.isfile('issue_data.json'): # Comment this out if the json file has broken data.
        get_all_issues()
    f = open('issue_data.json', 'r')
    data = json.loads(f.read())
    f.close()
    issue_nodes = {}
    for issue in data['issues']:
        node = Issue('issue', issue['number'], issue['title'], issue['body'], issue['comments'], issue['state'], issue['createdAt'], issue['closedAt'], issue['url'], issue['milestone'])
        issue_nodes[node.number] = node
    return issue_nodes

# Parses the data from the json files and creates a dictionary of graph nodes, where the key is the issue/pr number.
def build_pr_nodes():
    # Get all issues from the github api and write them to a json file.
    if not os.path.isfile('pr_data.json'):# Comment this out if the json file has broken data.
        get_all_prs() 
    f = open('pr_data.json', 'r')
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
    if not os.path.isfile('commit_data.json'):# Comment this out if the json file has broken data.
        get_all_commits() 
    f = open('commit_data.json', 'r')
    data = json.loads(f.read())
    f.close()
    commit_nodes = {}
    for commit in data['commits']:
        node = Commit('commit', commit['oid'], commit['message'], commit['committedDate'], commit['url'])
        commit_nodes[node.node_id] = node
    return commit_nodes

# Class representing graph nodes. Each node represents a software artifact (issue, pull request, requirement, commit).
class Node:
    def __init__(self, node_type, node_id, url):
        self.node_type = node_type
        self.node_id = node_id
        self.url = url
        self.traces = [] # List of nodes that this node traces to.	

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
        super().__init__(node_type, number, url)
        self.number = number
        self.title = title
        self.body = body
        self.comments = comment_parser(comments)
        self.number_of_comments = len(comments)
        self.state = state
        self.time_to_finish = time_to_finish(created, closed)
        self.milestone = milestone

class PullRequest(Issue):
    def __init__(self, node_type, number, title, body, comments, state, created, closed, url, milestone, related_commits):
        super().__init__(node_type, number, title, body, comments, state, created, closed, url, milestone)
        self.related_commits = related_commits

class Commit(Node):
    def __init__(self, node_type, id, message, committedDate, url):
        # TODO: Maybe add more info about the commit, like the files changed, additions, deletions, etc.
        # File change patches are not available in the graphQL API, so we need to use the GitHub API to get them, if necessary
        super().__init__(node_type, id, url)
        self.message = message
        tempDate = committedDate.replace('T', ' ').replace('Z', '')
        self.committedDate = datetime.datetime.strptime(tempDate, '%Y-%m-%d %H:%M:%S')

# Class representing the graph of software artifacts.
class Graph:
    def __init__(self):
        self.nodes = {}
        self.issue_nodes = build_issue_nodes()
        self.pr_nodes, self.commit_nodes = build_pr_nodes()
        self. commit_nodes = self.commit_nodes | build_commit_nodes()

    def __str__(self):
        return f"Graph with {len(self.nodes)} nodes."
    
graph = Graph()

for i in graph.issue_nodes:
    title = graph.issue_nodes[i].title
    print(title)
print(len(graph.issue_nodes))