import sys
import re
import json
from traceGraph import Graph
sys.path.append('..')
from keyword_extractors.dependency_parsing_custom_pipeline import custom_extractor
from neo4j_connection import create_req_issue_traces

word_regex = r'\b{0}\b'
verbobj_regex = r'\b{0}\s((?:[\w,;:\'\"`]+\s)*){1}\b'
noun_phrase_regex = r'\b{0}\s{1}\b'

def regex_match(regex):
    return re.compile(regex, flags=re.IGNORECASE).search

def issue_text(issue):
    issue['text'] = issue['title'] + ' ' + issue['body']
    # add the comments to the text
    for comment in issue['comment_list']:
        issue['text'] += ' ' + comment

def search_keyword(issue_nodes, regex):
    # This can be optimized by using multi-threading !!!
    start = time.time()
    found_nodes = set()

    for issue in issue_nodes:
        try:
            match = regex_match(regex)(issue.text)
        except Exception as e:
            print(str(e))
            print(issue.number)
        if match != None:
            # print(match, node.node_id)
            found_nodes.add(issue.number)
    end = time.time()
    #print("Time taken to search for keyword: ", end - start)
    return list(found_nodes)

def search_keyword_list(issue_nodes, keyword_list, req_number):
    
    found_nodes = []
    for keyword in keyword_list['verbs']:
        result = search_keyword(issue_nodes, word_regex.format(keyword))
        found_nodes.append((keyword, result, 0.5))
        #create_req_issue_traces(req_number, found_nodes['verbs'], 0.5, keyword)
    for keyword in keyword_list['verb-objects']:
        keywords = keyword.split()
        result = search_keyword(issue_nodes, verbobj_regex.format(keywords[0], keywords[1]))
        found_nodes.append((keyword, result, 1))
        #create_req_issue_traces(req_number, found_nodes['verb-objects'], 1, keyword)
    for keyword in keyword_list['nouns']:
        result = search_keyword(issue_nodes, word_regex.format(keyword))
        found_nodes.append((keyword, result, 0.5))
        #create_req_issue_traces(req_number, found_nodes['nouns'], 0.5, keyword)
    for keyword in keyword_list['noun-objects']:
        keywords = keyword.split()
        result = search_keyword(issue_nodes, noun_phrase_regex.format(keywords[0], keywords[1]))
        found_nodes.append((keyword, result, 1))
        #create_req_issue_traces(req_number, found_nodes['noun-objects'], 1, keyword)
    # found_nodes = [(keyword,issue_nodes,weight), ...)]
    return found_nodes

import time

def trace(repo_number):
    req_file = open(f"data_group{repo_number}/group{repo_number}_requirements.txt", "r", encoding="utf-8")
    start_all = time.time()
    graph = Graph(repo_number)
    count = 0
    total_search_time = 0
    total_extract_time = 0
    req_to_issue = {}
    for line in req_file:
        line = line.split(' ', 1)
        req_number = line[0]
        desc = line[1]

        start = time.time()
        token_dict = custom_extractor(desc, "../keyword_extractors/SmartStopword.txt")
        total_extract_time += time.time() - start

        start = time.time()
        req_to_issue[req_number] = search_keyword_list(graph.issue_nodes.values(), token_dict, req_number)
        total_search_time += time.time() - start
        
        count += 1
    create_req_issue_traces(req_to_issue)
    print("Average time taken to extract keywords per requirement: ", total_extract_time/count)   
    print("Average time taken to search keywords per requirement: ", total_search_time/count)
    end = time.time()
    print("Time taken to create traces: ", end - start_all)
        

trace(3)