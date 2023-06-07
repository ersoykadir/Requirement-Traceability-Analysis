"""
Kadir Ersoy - Ecenur Sezer
Requirements Traceability Tool

Reads artifact data from json files and creates neo4j nodes.
"""

import json
from neo4j.time import Date

from artifacts.artifacts import get_repo_creation_date
from trace_util.neo4j_connection import neo4jConnector
from config import Config

repo_creation_date = None

# Parses the comments of an issue or pull request.
def comment_parser(comments):
    comment_list = []
    comments = comments['nodes']
    for comment in comments:
        comment_list.append(comment['body'])
    return comment_list

# Parses the data from the issue file and creates neo4j nodes.
def build_issue_nodes():
    issue_data_fname = f'data_{Config().repo_name}/issues_data.json'
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
        
        # Concatenate the title, body and comments to create a single text property.
        issue['text'] = issue['title'] + ' ' + issue['body']
        for comment in issue['comment_list']:
            issue['text'] += ' ' + comment

        # Convert the dates to neo4j compatible format
        issue['createdAt'] = Date.from_iso_format(issue['createdAt'][:10])
        if(issue['closedAt'] is not None):
            issue['closedAt'] = Date.from_iso_format(issue['closedAt'][:10])

        # Calculate the weeks passed since the repo was created
        issue['created_week'] = (issue['createdAt'] - Date.from_iso_format(repo_creation_date[:10])).days // 7
        issue['closed_week'] = None
        if(issue['closedAt'] is not None):
            issue['closed_week'] = (issue['closedAt'] - Date.from_iso_format(repo_creation_date[:10])).days // 7

    # Create neo4j nodes 
    result = neo4jConnector().create_artifact_nodes(data['issues'], 'Issue')

# Parses the commits of a pull request.
# Not used in the current version. Commits are not held as pr properties, but as separate nodes.
def commit_parser(related_commits):
    commit_ids = []
    related_commits = related_commits['nodes']
    for commit in related_commits:
        cm = commit['commit']
        commit_ids.append(cm['oid'])
    return commit_ids

# Parses the data from the pull requests file and creates neo4j nodes.
def build_pr_nodes():
    pr_data_fname = f'data_{Config().repo_name}/pullRequests_data.json'
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

        # Concatenate the title, body and comments to create a single text property.
        pr['text'] = pr['title'] + ' ' + pr['body']
        for comment in pr['comment_list']:
            pr['text'] += ' ' + comment
        
        # Convert the dates to neo4j compatible format
        pr['createdAt'] = Date.from_iso_format(pr['createdAt'][:10])
        if(pr['closedAt'] is not None):
            pr['closedAt'] = Date.from_iso_format(pr['closedAt'][:10])

        # Calculate the weeks passed since the repo was created
        pr['created_week'] = (pr['createdAt'] - Date.from_iso_format(repo_creation_date[:10])).days // 7
        pr['closed_week'] = None
        if(pr['closedAt'] is not None):
            pr['closed_week'] = (pr['closedAt'] - Date.from_iso_format(repo_creation_date[:10])).days // 7
    
    # Create neo4j nodes
    result = neo4jConnector().create_artifact_nodes(data['pullRequests'], 'PullRequest')

# Parses the data from the commit file and creates neo4j nodes.
def build_commit_nodes():
    commit_data_fname = f'data_{Config().repo_name}/commits_data.json'
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

        # Convert the dates to neo4j compatible format
        commit['createdAt'] = Date.from_iso_format(commit['committedDate'][0:10])
        commit['closedAt'] = Date.from_iso_format(commit['committedDate'][0:10])

        # Calculate the weeks passed since the repo was created
        commit['created_week'] = (commit['createdAt'] - Date.from_iso_format(repo_creation_date[:10])).days // 7
        commit['closed_week'] = None
        if(commit['closedAt'] is not None):
            commit['closed_week'] = (commit['closedAt'] - Date.from_iso_format(repo_creation_date[:10])).days // 7

    # Create neo4j nodes
    result = neo4jConnector().create_artifact_nodes(data['commits'], 'Commit')

# Parses the data from the requirements file and creates neo4j nodes.
def build_requirement_nodes():
    data_fname = f'data_{Config().repo_name}/requirements_data.json'
    f = open(data_fname, 'r')
    data = json.loads(f.read())
    f.close()
    for requirement in data['requirements']:
        requirement['text'] = requirement['description']
    # Create neo4j nodes
    result = neo4jConnector().create_artifact_nodes(data['requirements'], 'Requirement')

import sys, time
"""
    Creates the neo4j nodes for the issues, pull requests, commits and requirements.
"""
def create_neo4j_nodes():
    global repo_creation_date
    repo_creation_date = get_repo_creation_date()

    start = time.time()

    build_issue_nodes()
    build_pr_nodes()
    build_commit_nodes()
    build_requirement_nodes()

    # Create indexes for faster querying
    neo4jConnector().create_indexes('Issue', 'number')
    neo4jConnector().create_indexes('PullRequest', 'number')
    neo4jConnector().create_indexes('Commit', 'number')
    neo4jConnector().create_indexes('Requirement', 'number')

    end = time.time()
    print(f"Time elapsed for creating neo4j nodes: {end-start}")