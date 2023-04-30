import json
from neo4j_connection import create_artifact_nodes, create_single_artifact_node

# Parses the comments of an issue or pull request.
def comment_parser(comments):
    comment_list = []
    comments = comments['nodes']
    for comment in comments:
        comment_list.append(comment['body'])
    return comment_list

# Parses the data from the json files and creates a dictionary of graph nodes, where the key is the issue/pr number.
def build_issue_nodes(repo_number):
    # Get all issues from the github api and write them to a json file.
    issue_data_fname = f'data_group{repo_number}/issues_data.json'
    f = open(issue_data_fname, 'r')
    data = json.loads(f.read())
    f.close()
    for issue in data['issues']:
        # if issue['number'] < issue_number_threshold: # Skip the issues that were created in 352.
        #     # remove the issue from the list
        #     continue

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

    # Create neo4j nodes from data['issues']
    print(len(data['issues']))
    result = create_artifact_nodes(data['issues'], 'Issue')
    print(result)

# Parses the commits of a pull request.
def commit_parser(related_commits):
    commit_ids = []
    related_commits = related_commits['nodes']
    for commit in related_commits:
        # Create commit object and add its id to the commit list.
        cm = commit['commit']
        commit_ids.append(cm['oid'])
    print(len(commit_ids))
    return commit_ids

# Parses the data from the json files and creates a dictionary of graph nodes, where the key is the issue/pr number.
def build_pr_nodes(repo_number):
    # Get all issues from the github api and write them to a json file.
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
        pr['commit_list'] = commit_parser(pr['commits'])
        del pr['commits']

        pr['text'] = pr['title'] + ' ' + pr['body']
        # add the comments to the text
        for comment in pr['comment_list']:
            pr['text'] += ' ' + comment
    
    # Create neo4j nodes
    print(len(data['pullRequests']))
    result = create_artifact_nodes(data['pullRequests'], 'PullRequest')
    print(result)

# Parses the data from the json files and creates a dictionary of graph nodes, where the key is the commit id.
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
    # Create neo4j nodes
    print(len(data['commits']))
    result = create_artifact_nodes(data['commits'], 'Commit')
    print(result)

def build_requirement_nodes(repo_number):
    data_fname = f'data_group{repo_number}/requirements_data.json'
    f = open(data_fname, 'r')
    data = json.loads(f.read())
    f.close()
    for requirement in data['requirements']:
        requirement['text'] = requirement['description']

    # Create neo4j nodes
    print(len(data['requirements']))
    result = create_artifact_nodes(data['requirements'], 'Requirement')
    print(result)

import sys
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

if __name__ == '__main__':
    main()
    