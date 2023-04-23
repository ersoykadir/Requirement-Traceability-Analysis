from neo4j import GraphDatabase

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
    def create_person_tx(tx, name):
        query = ("CREATE (a:Person {name: $name, id: randomUUID()}) "
                "RETURN a.id AS node_id")
        result = tx.run(query, name=name)
        record = result.single()
        return record["node_id"]
    
    def create_person(self, name):
        with self.driver.session() as session:
            node_id = session.execute_write(self.create_person_tx, name)
    
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
    def create_issue_tx(tx, issues):
        query = ('''
                UNWIND $issues AS properties
                CREATE (n:Issue)
                SET n = properties
                RETURN n
                ''')
        result = tx.run(query, issues=issues)
        record = result.data()
        return record

    def create_issue(self, issues):
        with self.driver.session() as session:
            result = session.execute_write(self.create_issue_tx, issues)
            print(result)

def create_issue_nodes(issues):
    try:
        neo = neo4jConnector("bolt://localhost:7687", "neo4j", "password")
        #print(issues)
        neo.create_issue(issues)
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
