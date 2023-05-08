"""
Kadir Ersoy - Ecenur Sezer
Requirements Traceability Tool

Acquires software artifacts(issue, pr, commmit, requirement) and writes them to json files.
"""

import os
import requests
import json
from graphql_templates import ISSUE_queryTemplate, PR_queryTemplate, COMMIT_queryTemplate
from dotenv import load_dotenv
load_dotenv()

username = os.getenv('GITHUB_USERNAME')
token = os.getenv('GITHUB_TOKEN')
print(username, token)

# Acquires data from the github graphql api, given a graphql query.
def get_data_from_api(body):
    global username, token
    url = 'https://api.github.com/graphql'
    r = requests.post(url = url, json = {"query":body}, auth=(username, token))
    data = r.json()
    #print(data)
    return data

# Gets a page of issues, appends them to the global issues list, and returns the hasNextPage and endCursor values.
def get_issue_page(body):
    data = get_data_from_api(body)
    issue_data = (data['data']['repository']['issues']['nodes'])
    hasNextPage = data['data']['repository']['issues']['pageInfo']['hasNextPage']
    endCursor = data['data']['repository']['issues']['pageInfo']['endCursor']
    return issue_data, hasNextPage, endCursor

# Gets a page of pull requests, appends them to the global pullRequests list, and returns the hasNextPage and endCursor values.
def get_pr_page(body):
    data = get_data_from_api(body)
    pull_request_data = (data['data']['repository']['pullRequests']['nodes'])
    hasNextPage = data['data']['repository']['pullRequests']['pageInfo']['hasNextPage']
    endCursor = data['data']['repository']['pullRequests']['pageInfo']['endCursor']
    return pull_request_data, hasNextPage, endCursor

# Gets a page of commits, appends them to the global commits list, and returns the hasNextPage and endCursor values.
def get_commit_page(body):
    data = get_data_from_api(body)
    commit_data = (data['data']['repository']['ref']['target']['history']['nodes'])
    hasNextPage = data['data']['repository']['ref']['target']['history']['pageInfo']['hasNextPage']
    endCursor = data['data']['repository']['ref']['target']['history']['pageInfo']['endCursor']
    return commit_data, hasNextPage, endCursor

get_artifact_page = {
    'issues': get_issue_page,
    'pullRequests': get_pr_page,
    'commits': get_commit_page
}

# graphql query templates for each artifact type
artifact_template = {
    'issues': ISSUE_queryTemplate,
    'pullRequests': PR_queryTemplate,
    'commits': COMMIT_queryTemplate
}

# Gets all issues, page by page, and writes them to a json file.
def get_all_pages(artifact_type, repo_owner, repo_number, repo_name):
    if os.path.exists(f'data_group{repo_number}/{artifact_type}_data.json'):
        print(f'{artifact_type} already exists.')
        return
    template = artifact_template[artifact_type]
    get_page = get_artifact_page[artifact_type]
    pages = []
    hasNextPage, endCursor = True, "null"
    
    # Traverse the pages
    while(hasNextPage):
        if endCursor != "null":
            endCursor = "\"" + endCursor + "\""
        # Update the query with the new endCursor
        query = template.substitute(owner=repo_owner, name=repo_name, cursor=endCursor)
        # Get the next page of issues
        page_data, hasNextPage, endCursor = get_page(query)
        pages = pages + page_data
    
    # Write the issues to a json file
    data_fname = f'data_group{repo_number}/{artifact_type}_data.json'
    f = open(data_fname, 'w')
    dump = {artifact_type: pages}
    f.write(json.dumps(dump, indent=4))
    f.close()

def get_requirements(repo_number):
    if os.path.exists(f'data_group{repo_number}/requirements_data.json'):
        print('requirements already exists.')
        return
    requirements_file_name = f'data_group{repo_number}/group{repo_number}_requirements.txt'
    f = open(requirements_file_name, 'r', encoding='utf-8', errors='ignore')
    data = f.readlines()
    f.close()

    requirements = [] # List of requirement dictionaries, to be written to a json file

    for line in data:
        # Assuming that the requirement number is the first word in the line
        if len(line) == 0:
            continue
        req = line.split(' ', 1)
        req_number = req[0].strip()
        if req_number[-1] == '.':
            req_number = req_number[:-1]
        req_description = req[1]
        req_dict = {
            'number': req_number,
            'description': req_description,
            'parent': '.'.join(req_number.split('.')[:-1])
        }
        requirements.append(req_dict)
    
    # Write the requirements to a json file
    data_fname = f'data_group{repo_number}/requirements_data.json'
    f = open(data_fname, 'w')
    dump = {'requirements': requirements}
    f.write(json.dumps(dump, indent=4))
    f.close()

import sys, time
def get_artifacts(repo_number):
    start = time.time()
    repo_owner = 'bounswe'
    repo_name = f'bounswe2022group{repo_number}'

    get_all_pages('issues', repo_owner, repo_number, repo_name)
    get_all_pages('pullRequests', repo_owner, repo_number, repo_name)
    get_all_pages('commits', repo_owner, repo_number, repo_name)
    get_requirements(repo_number)
    end = time.time()
    print(f"Time elapsed for acquiring artifacts from github: {end-start}")

def main():
    start = time.time()
    repo_number = sys.argv[1]
    repo_owner = 'bounswe'
    repo_name = f'bounswe2022group{repo_number}'
    
    get_all_pages('issues', repo_owner, repo_number, repo_name)
    get_all_pages('pullRequests', repo_owner, repo_number, repo_name)
    get_all_pages('commits', repo_owner, repo_number, repo_name)
    get_requirements(repo_number)
    end = time.time()
    print(f"Time elapsed: {end-start}")

if __name__ == "__main__":
    main()