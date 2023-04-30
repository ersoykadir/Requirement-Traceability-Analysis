import sys
sys.path.append('..')
from keyword_extractors.dependency_parsing_custom_pipeline import custom_extractor
from neo4j_connection import create_req_issue_traces

word_regex = '.*\\b{0}\\b.*'
verbobj_regex = '.*\\b{0}\\s((?:[\\w,;:\\\'\\"`]+\\s)*){1}\\b.*'
noun_phrase_regex = '.*\\b{0}\\s{1}\\b.*'

def trace_finder(keywords, req_number):
    
    for keyword in keywords['verbs']:
        result = create_req_issue_traces(word_regex.format(keyword), req_number)
    for keyword in keywords['verb-objects']:
        pass
        #keyword = keyword.split()
        #result = create_req_issue_traces(verbobj_regex.format(keyword[0], keyword[1]), req_number)
    for keyword in keywords['nouns']:
        result = create_req_issue_traces(word_regex.format(keyword), req_number)
    for keyword in keywords['noun-objects']:
        pass
        #keyword = keyword.split()
        #result = create_req_issue_traces(noun_phrase_regex.format(keyword[0], keyword[1]), req_number)


def trace(repo_number):
    req_file = open(f"data_group{repo_number}/group{repo_number}_requirements.txt", "r", encoding="utf-8")
    for line in req_file:
        line = line.split(' ', 1)
        req_number = line[0]
        desc = line[1]
        token_dict = custom_extractor(desc, "../keyword_extractors/SmartStopword.txt")
        #trace_finder(token_dict, req_number)
        create_req_issue_traces(token_dict, req_number)
        break

trace(3)