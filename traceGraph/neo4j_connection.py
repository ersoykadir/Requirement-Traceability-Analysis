import datetime
from neo4j import GraphDatabase
from dotenv import load_dotenv
load_dotenv()
import os

neo4j_password = os.getenv('NEO4J_PASSWORD')

word_regex = '.*\\b{0}\\b.*'
verbobj_regex = '.*\\b{0}\\s((?:[\\w,;:\\\'\\"`]+\\s)*){1}\\b.*'
noun_phrase_regex = '.*\\b{0}\\s{1}\\b.*'

class neo4jConnector:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def print_greeting(self, message):
        with self.driver.session() as session:
            greeting = session.execute_write(self._create_and_return_greeting, message)
            print(greeting)

    @staticmethod
    def _create_and_return_greeting(tx, message):
        result = tx.run("CREATE (a:Greeting) "
                        "SET a.message = $message "
                        "RETURN a.message + ', from node ' + id(a)", message=message)
        return result.data()

    @staticmethod
    def create_issue_from_file_tx(tx):
        query = ('''CALL apoc.load.json('file:///data.json') YIELD value as v 
                UNWIND v.issues AS properties
                CREATE (n:Issue)
                SET n = properties
                RETURN n
                ''')
        
        result = tx.run(query)
        record = result.data()
        return record

    def create_issue_from_file(self):
        with self.driver.session() as session:
            result = session.execute_write(self.create_issue_from_file_tx)

    @staticmethod
    def create_artifact_tx(tx, artifacts, label):
        query = (f'''
                UNWIND $artifacts AS properties
                create (n: {label} )
                SET n = properties
                RETURN n
                ''').format(label=label)
        result = tx.run(query, artifacts=artifacts, label=label)
        record = result.data()
        return record

    def create_artifact(self, artifacts, label):
        with self.driver.session() as session:
            result = session.execute_write(self.create_artifact_tx, artifacts, label)
    
    @staticmethod
    def create_trace_tx(tx, req_number, node_list, weight, keyword, artifact_label):
        query = ('''
                match (r:Requirement)
                where r.number = '{req_number}'
                with r
                UNWIND {node_list} AS node_numbers
                match (i:{artifact_label})
                where i.number= node_numbers
                create (i)<-[t:tracesTo]-(r)
                set t.weight = {weight}
                set t.keyword = '{keyword}'
                return *
                ''')
        
        # for req_number in req_issue_trace:
        #     for tuple in req_issue_trace[req_number]:
        #         keyword, node_list, weight = tuple
        query = query.format(req_number=req_number, node_list=node_list, weight=weight, keyword=keyword, artifact_label=artifact_label)
        result = tx.run(query)
        record = result.data()
        #return record

    def create_trace(self, req_issue_trace, artifact_label):
        try:
            with self.driver.session() as session:
                print("connecting to neo4j")
                # if artifact_label == 'Issue':
                #     print(req_issue_trace)
                # Send query for each requirement instead of for each keyword!
                for req_number in req_issue_trace:
                    for tuple in req_issue_trace[req_number]:
                        keyword, node_list, weight = tuple
                        if len(node_list) > 0:
                            result = session.execute_write(self.create_trace_tx, req_number, node_list, weight, keyword, artifact_label)
                # result = session.execute_write(self.create_req_issue_trace_tx, req_issue_trace, artifact_label)
        except Exception as e:
            return 'Error: ' + str(e)  
    
    @staticmethod
    def create_trace_v2_tx(tx, req_number, artifact_key_pairs, artifact_label):
        query = ('''
                match (r:Requirement)
                where r.number = '{req_number}'
                with r
                UNWIND {artifact_key_pairs} AS art_key_pair
                match (i:{artifact_label})
                where i.number= art_key_pair[0]
                create (i)<-[t:tracesTo]-(r)
                set t.keywords = art_key_pair[1][0]
                set t.weight = art_key_pair[1][1]
                return *
                ''')
        query = query.format(req_number=req_number, artifact_key_pairs=artifact_key_pairs, artifact_label=artifact_label)
        result = tx.run(query)
        record = result.data()
        #return record

    def create_trace_v2(self, trace, artifact_label):
        try:
            with self.driver.session() as session:
                print("connecting to neo4j")
                # if artifact_label == 'Issue':
                #     print(req_issue_trace)
                # Send query for each requirement instead of for each keyword!
                for req_number in trace:
                    req_trace = trace[req_number]
                    artifacts = list(req_trace.keys())
                    keywords = list(req_trace.values())
                    artifact_key_pairs = [[i, j] for i, j in zip(artifacts, keywords)]
                    result = session.execute_write(self.create_trace_v2_tx, req_number, artifact_key_pairs, artifact_label)
                # result = session.execute_write(self.create_req_issue_trace_tx, req_issue_trace, artifact_label)
        except Exception as e:
            return 'Error: ' + str(e) 

    @staticmethod
    def create_trace_w2v_tx(tx, req_number, node_list, artifact_label):
        query = ('''
                match (r:Requirement)
                where r.number = '{req_number}'
                with r
                UNWIND {node_list} AS node_numbers
                match (i:{artifact_label})
                where i.number= node_numbers
                create (i)<-[t:tracesTo]-(r)
                return *
                ''')
        query = query.format(req_number=req_number, node_list=node_list, artifact_label=artifact_label)
        result = tx.run(query)
        record = result.data()
        #return record

    def create_trace_w2v(self, req_issue_trace, artifact_label):
        try:
            with self.driver.session() as session:
                print("connecting to neo4j")
                for req_number in req_issue_trace:
                    node_list = req_issue_trace[req_number]
                    result = session.execute_write(self.create_trace_w2v_tx, req_number, node_list, artifact_label)
        except Exception as e:
            return 'Error: ' + str(e)  

    @staticmethod
    def link_commit_pr_tx(tx):
        query = ('''
                MATCH (n:Commit), (p:PullRequest)
                where n.associatedPullRequests = p.number
                create (p)-[t:relatedCommit]->(n)
                RETURN * 
                ''')
        query = query.format()
        result = tx.run(query)
        record = result.data()

    def link_commit_pr(self):
        try:
            with self.driver.session() as session:
                print("connecting to neo4j")
                result = session.execute_write(self.link_commit_pr_tx)
        except Exception as e:
            return 'Error: ' + str(e)  
        
    @staticmethod
    def clean_artifacts_tx(tx, threshold, label):
        query = (f'''
                MATCH (n:{label})
                where n.number < {threshold}
                delete n
                ''').format(label=label, threshold=threshold)
        result = tx.run(query)
        record = result.data()
        return record

    def clean_artifacts(self, threshold, label):
        with self.driver.session() as session:
            result = session.execute_write(self.clean_artifacts_tx, threshold, label)

    @staticmethod
    def filter_artifacts_tx(tx, date):
        query_issue = (f'''
                    Match(n:Issue) 
                    where datetime(n.createdAt) <= datetime("{date}")
                    delete n
                ''').format(date=date)
        print(query_issue)
        query_pr = (f'''
                    Match(n:PullRequest) 
                    where datetime(n.createdAt) <= datetime("{date}")
                    delete n
                ''').format(date=date)
        query_commit = (f'''
                    Match(n:Commit) 
                    where datetime(n.committedDate) <= datetime("{date}")
                    delete n
                ''').format(date=date)
        result = tx.run(query_issue)
        result = tx.run(query_pr)
        result = tx.run(query_commit)
        record = result.data()
        return record

    def filter_artifacts(self, date):
        with self.driver.session() as session:
            result = session.execute_write(self.filter_artifacts_tx, date)

    @staticmethod
    def clean_all_data_tx(tx):
        query = ('''
                MATCH (n)
                detach delete n
                ''')
        result = tx.run(query)
        record = result.data()
        return record

    def clean_all_data(self):
        with self.driver.session() as session:
            result = session.execute_write(self.clean_all_data_tx)

def create_artifact_nodes(artifacts, label):
    try:
        neo = neo4jConnector("bolt://localhost:7687", "neo4j", neo4j_password)
        neo.create_artifact(artifacts, label)
        neo.close()
    except Exception as e:
        return 'Error: ' + str(e) + ' for label: ' + label
import time
def create_traces(neo:neo4jConnector, req_issue_trace, artifact_label):
    start = time.time() 
    try:
        neo.create_trace(req_issue_trace, artifact_label)
    except Exception as e:
        return 'Error: ' + str(e) 
    end = time.time()
    print(f"Time taken to connect neo4j and create traces for {artifact_label}: ", end - start)

def create_traces_v2(neo:neo4jConnector, trace, artifact_label):
    start = time.time() 
    try:
        neo.create_trace_v2(trace, artifact_label)
    except Exception as e:
        return 'Error: ' + str(e) 
    end = time.time()
    print(f"Time taken to connect neo4j and create traces for {artifact_label}: ", end - start)

def create_traces_w2v(neo:neo4jConnector, req_issue_trace, artifact_label):
    start = time.time() 
    try:
        neo.create_trace_w2v(req_issue_trace, artifact_label)
    except Exception as e:
        return 'Error: ' + str(e) 
    end = time.time()
    print(f"Time taken to connect neo4j and create traces for {artifact_label}: ", end - start)

def link_commits_prs(neo:neo4jConnector):
    start = time.time() 
    try:
        neo.link_commit_pr()
    except Exception as e:
        return 'Error: ' + str(e) 
    end = time.time()
    print(f"Time taken to connect neo4j and link commits and prs: ", end - start)

def clean_artifact_nodes(neo:neo4jConnector, threshold, label):
    try:
        neo.clean_artifacts(threshold, label)
    except Exception as e:
        return 'Error: ' + str(e)
    
def clean_all_data(neo:neo4jConnector):
    try:
        neo = neo4jConnector("bolt://localhost:7687", "neo4j", neo4j_password)
        neo.clean_all_data()
    except Exception as e:
        return 'Error: ' + str(e)
    
def filter_artifact(date:datetime):
    try:
        neo = neo4jConnector("bolt://localhost:7687", "neo4j", neo4j_password)
        neo.filter_artifacts(date)
        neo.close()
    except Exception as e:
        return 'Error: ' + str(e)
    

    
