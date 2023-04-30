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
            print(result)

    @staticmethod
    def create_artifact_tx(tx, artifacts, label):
        query = (f'''
                UNWIND $artifacts AS properties
                CREATE (n:{label})
                SET n = properties
                RETURN n
                ''').format(label=label)
        result = tx.run(query, artifacts=artifacts)
        record = result.data()
        return record

    def create_artifact(self, artifacts, label):
        with self.driver.session() as session:
            result = session.execute_write(self.create_artifact_tx, artifacts, label)
            #print(result)
    
    @staticmethod
    def create_req_issue_trace_tx(tx, regex, number):
        query = ('''
                match (i:Issue)
                where i.text =~ '$regex'
                with i
                match (r:Requirement {number: '$number'})
                create (i)<-[t:tracesTo]-(r)
                return *
                ''')
        print(query)
        result = tx.run(query, regex=regex, number=number)
        record = result.data()
        return record

    def create_req_issue_trace(self, token_dict, number):
        try:
            with self.driver.session() as session:
                print("connecting to neo4j")
                for keyword in token_dict['verbs']:
                    print(keyword)
                    result = session.execute_write(self.create_req_issue_trace_tx, word_regex.format(keyword), number)
                    print(result)
        except Exception as e:
            return 'Error: ' + str(e) + ' ' + number
    @staticmethod
    def create_single_artifact_tx(tx, properties, label):
        query = (f'''
                CREATE (n:{label})
                SET n = $properties
                RETURN n
                ''').format(label=label)
        result = tx.run(query, properties=properties)
        record = result.data()
        return record

    def create_single_artifact(self, properties, label):
        with self.driver.session() as session:
            result = session.execute_write(self.create_artifact_tx, properties, label)
            #print(result)

def create_artifact_nodes(artifacts, label):
    try:
        neo = neo4jConnector("bolt://localhost:7687", "neo4j", "password")
        #print(issues)
        neo.create_artifact(artifacts, label)
        neo.close()
    except Exception as e:
        return 'Error: ' + str(e)

def create_req_issue_traces(token_dict, number):
    try:
        neo = neo4jConnector("bolt://localhost:7687", "neo4j", "password")
        #print(issues)
        neo.create_req_issue_trace(token_dict, number)
        neo.close()
    except Exception as e:
        return 'Error: ' + str(e) + ' ' + + number

def create_single_artifact_node(properties, label):
    try:
        neo = neo4jConnector("bolt://localhost:7687", "neo4j", "password")
        #print(issues)
        neo.create_single_artifact(properties, label)
        neo.close()
    except Exception as e:
        return 'Error: ' + str(e)

# if __name__ == "__main__":
#     greeter = HelloWorldExample("bolt://localhost:7687", "neo4j", "password")
#     greeter.print_greeting("hello, world")
#     greeter.close()

#     greeter1 = HelloWorldExample("bolt://localhost:7687", "neo4j", "password")
#     greeter1.create_issue()
#     greeter1.close()
