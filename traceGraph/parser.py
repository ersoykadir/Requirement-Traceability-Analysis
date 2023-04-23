import json
from neo4j_connection import create_issue_nodes

repo_owner = 'bounswe'
repo_number = 3
repo_name = f'bounswe2022group{repo_number}'

if repo_number == 2:
    issue_number_threshold = 309 # for group 2
elif repo_number == 3:
    issue_number_threshold = 258 # for group 3
else:
    raise Exception("Invalid repo number")

# Parses the comments of an issue or pull request.
def comment_parser(comments):
    comment_list = []
    comments = comments['nodes']
    for comment in comments:
        comment_list.append(comment['body'])
    return comment_list

# Parses the data from the json files and creates a dictionary of graph nodes, where the key is the issue/pr number.
def build_issue_nodes():
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

    # Create neo4j nodes from data['issues']
    result = create_issue_nodes(data['issues'])
    #print(result)

def main():
    build_issue_nodes()

if __name__ == '__main__':
    main()
    