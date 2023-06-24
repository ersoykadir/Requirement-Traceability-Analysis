"""
Requirements Traceability Tool

Node parser for the util graph.
Utilized for representing each artifact as node and finding trace links between them.
TODO: Get rid of the util graph and use only the neo4j graph.
"""

import json
from .Node import Issue, PullRequest, Commit, Requirement
from config import Config

# Parses the commits of a pull request.
def commit_parser(related_commits):
    commit_text = ''
    related_commits = related_commits['nodes']
    for commit in related_commits:
        # Create commit object and add its id to the commit list.
        cm = commit['commit']
        commit_text += cm['message'] + '. '
    return commit_text

# Parses the data from the issue file and creates a dictionary of graph nodes, where the key is the issue number.
def build_issue_nodes():
    issue_data_fname = f'data_{Config().repo_name}/issues_data.json'
    f = open(issue_data_fname, 'r')
    data = json.loads(f.read())
    f.close()
    issue_nodes = {}
    for issue in data['issues']:
        if issue['createdAt'] < Config().filter_nodes_before_date:
            continue
        node = Issue('issue', issue['number'], issue['title'], issue['body'], issue['comments'], issue['state'], issue['createdAt'], issue['closedAt'], issue['url'], issue['milestone'])
        issue_nodes[node.number] = node
    return issue_nodes

# Parses the data from the pull requests file and creates a dictionary of graph nodes, where the key is the pr number.
def build_pr_nodes():
    pr_data_fname = f'data_{Config().repo_name}/pullRequests_data.json'
    f = open(pr_data_fname, 'r')
    data = json.loads(f.read())
    f.close()
    pr_nodes = {}
    for pr in data['pullRequests']:
        if pr['createdAt'] < Config().filter_nodes_before_date:
            continue
        node = PullRequest('pullRequest', pr['number'], pr['title'], pr['body'], pr['comments'], pr['state'], pr['createdAt'], pr['closedAt'], pr['url'], pr['milestone'], pr['commits'])
        pr_nodes[node.number] = node
        # Parse the commits of the pull request.
        # commit_text = commit_parser(pr['commits'])
        # node.text += commit_text
    return pr_nodes

# Parses the data from the commits file and creates a dictionary of graph nodes, where the key is the commit id.
def build_commit_nodes():
    commit_data_fname = f'data_{Config().repo_name}/commits_data.json'
    f = open(commit_data_fname, 'r')
    data = json.loads(f.read())
    f.close()
    commit_nodes = {}
    for commit in data['commits']:
        if commit['committedDate'] < Config().filter_nodes_before_date:
            continue
        associatedPullRequest = None
        if len(commit['associatedPullRequests']['nodes']) > 0:
            associatedPullRequest = commit['associatedPullRequests']['nodes'][0]['number']
        node = Commit('commit', commit['oid'], commit['message'], commit['committedDate'], commit['url'], associatedPullRequest)
        commit_nodes[node.number] = node
    return commit_nodes

# Parses the data from the requirements file and creates a dictionary of graph nodes, where the key is the requirement number.
def build_requirement_nodes():
    data_fname = f'data_{Config().repo_name}/requirements_data.json'
    f = open(data_fname, 'r')
    data = json.loads(f.read())
    f.close()
    requirement_nodes = {}
    for req in data['requirements']:
        node = Requirement('requirement', req['number'], req['description'])
        if Config().parent_mode and req['parent'] != "":
            node.parent = requirement_nodes[req['parent']]
        requirement_nodes[node.number] = node
    return requirement_nodes