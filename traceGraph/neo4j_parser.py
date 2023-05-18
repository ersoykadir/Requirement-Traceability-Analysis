"""
Kadir Ersoy - Ecenur Sezer
Requirements Traceability Tool

Reads artifact data from json files and creates neo4j nodes.
"""

import json
from neo4j_connection import create_artifact_nodes, create_indexes, neo4jConnector, neo4j_password
from neo4j.time import Date, DateTime


# Parses the comments of an issue or pull request.
def comment_parser(comments):
    comment_list = []
    comments = comments['nodes']
    for comment in comments:
        comment_list.append(comment['body'])
    return comment_list

# Parses the data from the issue file and creates neo4j nodes.
def build_issue_nodes(repo_number):
    issue_data_fname = f'data_group{repo_number}/issues_data.json'
    f = open(issue_data_fname, 'r')
    data = json.loads(f.read())
    f.close()
    for issue in data['issues']:
        # Since neo4j does not support dictionaries as properties, we need to convert the dictionaries to lists or strings.
        issue['commentCount'] = issue['comments']['totalCount']
        issue['comment_list'] = comment_parser(issue['comments'])   
        del issue['comments']
        if issue['milestone'] is not None:
            issue['milestone'] = issue['milestone']['description']
        
        issue['text'] = issue['title'] + ' ' + issue['body']
        # add the comments to the text
        for comment in issue['comment_list']:
            issue['text'] += ' ' + comment

        # Convert the dates to neo4j Date objects
        issue['createdAt'] = DateTime.from_iso_format(issue['createdAt'].replace('Z', '+00:00'))
        if(issue['closedAt'] is not None):
            issue['closedAt'] = DateTime.from_iso_format(issue['closedAt'].replace('Z', '+00:00'))

    # Create neo4j nodes from data['issues']
    result = create_artifact_nodes(data['issues'], 'Issue')

# Parses the commits of a pull request.
def commit_parser(related_commits):
    commit_ids = []
    related_commits = related_commits['nodes']
    for commit in related_commits:
        cm = commit['commit']
        commit_ids.append(cm['oid'])
    return commit_ids

# Parses the data from the pull requests file and creates neo4j nodes.
def build_pr_nodes(repo_number):
    pr_data_fname = f'data_group{repo_number}/pullRequests_data.json'
    f = open(pr_data_fname, 'r')
    data = json.loads(f.read())
    f.close()
    for pr in data['pullRequests']:
        # Since neo4j does not support dictionaries as properties, we need to convert the dictionaries to lists or strings.
        pr['commentCount'] = pr['comments']['totalCount']
        pr['comment_list'] = comment_parser(pr['comments'])   
        del pr['comments']
        if pr['milestone'] is not None:
            pr['milestone'] = pr['milestone']['description']

        # Parse the commits of the pull request.
        pr['commitCount'] = pr['commits']['totalCount']
        #pr['commit_list'] = commit_parser(pr['commits'])
        del pr['commits']

        pr['text'] = pr['title'] + ' ' + pr['body']
        # add the comments to the text
        for comment in pr['comment_list']:
            pr['text'] += ' ' + comment
        
        # Convert the dates to neo4j Date objects
        pr['createdAt'] = DateTime.from_iso_format(pr['createdAt'].replace('Z', '+00:00'))
        if(pr['closedAt'] is not None):
            pr['closedAt'] = DateTime.from_iso_format(pr['closedAt'].replace('Z', '+00:00'))
    
    # Create neo4j nodes
    result = create_artifact_nodes(data['pullRequests'], 'PullRequest')

# Parses the data from the commit file and creates neo4j nodes.
def build_commit_nodes(repo_number):
    commit_data_fname = f'data_group{repo_number}/commits_data.json'
    f = open(commit_data_fname, 'r')
    data = json.loads(f.read())
    f.close()
    for commit in data['commits']:
        if len(commit['associatedPullRequests']['nodes']) > 0:
            commit['associatedPullRequests'] = commit['associatedPullRequests']['nodes'][0]['number']
        else:
            commit['associatedPullRequests'] = None

        commit['text'] = commit['message']
        commit['number'] = commit['oid']
        commit['createdAt'] = DateTime.from_iso_format(commit['committedDate'].replace('Z', '+00:00'))
    # Create neo4j nodes
    result = create_artifact_nodes(data['commits'], 'Commit')

# Parses the data from the requirements file and creates neo4j nodes.
def build_requirement_nodes(repo_number):
    data_fname = f'data_group{repo_number}/requirements_data.json'
    f = open(data_fname, 'r')
    data = json.loads(f.read())
    f.close()
    for requirement in data['requirements']:
        requirement['text'] = requirement['description']

    # Create neo4j nodes
    result = create_artifact_nodes(data['requirements'], 'Requirement')

import sys, time

def create_neo4j_nodes(repo_number):
    start = time.time()
    if repo_number == 2:
        issue_number_threshold = 309 # for group 2
    elif repo_number == 3:
        issue_number_threshold = 258 # for group 3
    else:
        raise Exception("Invalid repo number")

    build_issue_nodes(repo_number)
    build_pr_nodes(repo_number)
    build_commit_nodes(repo_number)
    build_requirement_nodes(repo_number)

    # Create indexes
    neo = neo4jConnector("bolt://localhost:7687", "neo4j", neo4j_password)
    create_indexes(neo,'Issue', 'number')
    create_indexes(neo,'PullRequest', 'number')
    create_indexes(neo,'Commit', 'number')
    neo.close()
    end = time.time()
    print(f"Time elapsed for creating neo4j nodes: {end-start}")

def main():
    repo_number = int(sys.argv[1])

    if repo_number == 2:
        issue_number_threshold = 309 # for group 2
    elif repo_number == 3:
        issue_number_threshold = 258 # for group 3
    else:
        raise Exception("Invalid repo number")

    build_issue_nodes(repo_number)
    build_pr_nodes(repo_number)
    build_commit_nodes(repo_number)
    build_requirement_nodes(repo_number)

    # Create indexes
    neo = neo4jConnector("bolt://localhost:7687", "neo4j", neo4j_password)
    create_indexes(neo,'Issue', 'number')
    create_indexes(neo,'PullRequest', 'number')
    create_indexes(neo,'Commit', 'number')
    neo.close()

if __name__ == '__main__':
    main()
    