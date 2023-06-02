import datetime
from neo4j import GraphDatabase
from dotenv import load_dotenv
load_dotenv()
import os

neo4j_username = os.getenv('NEO4J_USERNAME')
neo4j_password = os.getenv('NEO4J_PASSWORD')
neo4j_uri = os.getenv('NEO4J_URI')

class neo4jConnector:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = object.__new__(cls)
            cls.instance.__initialized = False
        return cls.instance

    def __init__(self):
        if self.__initialized: return
        self.__initialized = True

        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_username, neo4j_password))

    def close(self):
        self.driver.close()

    @staticmethod
    def tx(tx, query, params):        
        result = tx.run(query, params)
        record = result.data()
        return record

    def execute_query(self, query, params=None):
        try:
            with self.driver.session() as session:
                result = session.execute_write(self.tx, query, params)
        except Exception as e:
            print(query, params)
            print(result)
            raise e

########################

def create_issue_from_json(json_file):
    query = ('''CALL apoc.load.json('$json_file') YIELD value as v 
        UNWIND v.issues AS properties
        CREATE (n:Issue)
        SET n = properties
        RETURN n
    ''')
    params = {'json_file': json_file}

    neo4jConnector().execute_query(query, params)

def create_artifact_nodes(artifacts, label):
    query = (f'''
        UNWIND $artifacts AS properties
        create (n: $label )
        SET n = properties
        RETURN n
    ''')
    params = {'artifacts': artifacts, 'label': label}

    neo4jConnector.execute_query(query, params)

def link_commits_prs():
    query = ('''
        MATCH (n:Commit), (p:PullRequest)
        where n.associatedPullRequests = p.number
        create (p)-[t:relatedCommit]->(n)
        RETURN * 
    ''')
    neo4jConnector().execute_query(query)

def create_indexes(label, field):
    query = (f'''
        CREATE INDEX ON :$label($field)
    ''')
    params = { "label": label, "field": field }
    
    neo4jConnector().execute_query(query, params)

def clean_all_data():
    query = ('''
        MATCH (n)
        detach delete n
    ''')   
    
    neo4jConnector().execute_query(query)

def filter_artifacts(date):
    query_issue = (f'''
        Match(n:Issue) 
        where date(n.createdAt) <= date("$date")
        delete n
    ''')
    query_pr = (f'''
        Match(n:PullRequest) 
        where date(n.createdAt) <= date("$date")
        delete n
    ''')
    query_commit = (f'''
        Match(n:Commit) 
        where date(n.committedDate) <= date("$date")
        delete n
    ''')
    params = {'date': date}
    neo4jConnector().execute_query(query_issue, params)
    neo4jConnector().execute_query(query_pr, params)
    neo4jConnector().execute_query(query_commit, params)
    
def create_traces_v3(traces):
    query = (f'''
                UNWIND $traces AS trace
                MATCH (r:Requirement)
                WHERE r.number = trace[0]
                WITH r, trace[1] as trace_list
                unwind trace_list AS art_key_pair
                MATCH (i:PullRequest)
                WHERE i.number = art_key_pair[0]
                CREATE (i)<-[t:tracesTo]-(r)
                SET t.weight = art_key_pair[1][0]
                SET t.keywords = art_key_pair[1][1]
                RETURN *
            ''')
    params = {'traces': traces}
    neo4jConnector().execute_query(query, params)