
# Requirement Traceability Tool

This project creates a tool that identifies and visualizes the trace links for a software project given the requirements and software development repository.
[A short video explanining the architecture and the tool.](https://www.youtube.com/watch?v=DhbpC6D7EeE)

## Used Technologies

**Programming Language:** Python

**Graph DB:** Neo4j

  
## Authors

- [Ecenur Sezer](https://www.github.com/codingAku)
- [Kadir Ersoy](https://www.github.com/ersoykadir) 


  
## How to Run

The project needs Python=3.10 to operate. 
You can download it by clicking [here](https://www.python.org/downloads/release/python-3100/).

### Prepare virtual environment

It is recommended to use a virtual environment on Python using _venv_ library.

Clone the project using the following shell command.

```bash
  git clone https://github.com/ersoykadir/Requirement-Traceability-Analysis.git
```

Create a virtual environment,
```bash
  python -m venv /path_to_your_venv
```
and activate it.
<div style="text-align: center; display: grid; grid-template-columns: 1fr 1fr">
  <div>
  For Linux:

  ```bash
    . path_to_your_venv/bin/activate
  ```
  </div>
  <div>
  For Windows:

  ```bash
    path_to_your_venv\Scripts\activate
  ```
  </div>
</div>

Navigate to the root directory of the project and install the required dependencies.

```bash
  cd ./Requirement-Traceability-Analysis
  pip install -r requirements.txt
```
Navigate to the traceGraph directory:
```bash
cd traceGraph
```
Create a _.env_ file with the following content:
 
```bash
GITHUB_USERNAME= < your github username >
GITHUB_TOKEN= < your github token >
NEO4J_PASSWORD= password
NEO4J_USERNAME= neo4j
NEO4J_URI= bolt://localhost:7687
OPENAI_API_KEY= < your openai token >
PRETRAINED_MODEL_PATH= < path to your pre-trained word-vector model >
FILTER_BEFORE= < OPTIONAL, provide to filter out software artifacts before a certain date >
```
You can find a file named _.env.example_ as a template in the traceGraph directory. We have chosen neo4j/password as default credentials. Please don't change neo4j credential defaults, since they are also used while creating the neo4j docker, or update the docker-compose file as well.
OpenAI key token utilized for acquiring word embeddings from openai's text-embedding-ada-002 model. Also any pre-trained word-vectors can be used, providing its path. We have utilized word2vec's [GoogleNews-vectors-negative300](https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit?resourcekey=0-wjGZdNAUop6WykTtMip30g).

-----
### Prepare Neo4j server

A neo4j server is required to use our dashboard. We provide a docker compose file, assuming docker is installed, to fasten installation process. At the root directory of the project, run
```bash
  docker compose up -d
```

Alternative to dockerized version, [Neo4j Desktop](https://neo4j.com/download/) can also be used. Just don't forget to add [apoc](https://neo4j.com/labs/apoc/4.4/installation/) plugin.

-----
### Run the tool
Navigate to the traceGraph directory under the root.
```bash
cd ./traceGraph
```
---
BEWARE! If you want to use a repository apart from our example repositories, please provide the requirements.txt

Open a repository named data_reponame and create requirements.txt
```
cd data_reponame
touch requirements.txt
```
Then you can copy your projects requirements into it.

---

Run _.main.py_ with three system arguments; 

```bash
python ./main.py <git_repo> <search_method> <options>
```

- <git_repo>  repo_owner/repo_name 
  - e.g. ersoykadir/Requirement-Traceability-Analysis

- <search_method> indicates the method used for searching traces.
  - keyword:  Keyword extraction method for capturing traces.
  - tf-idf vector: tf-idf vector method for capturing traces.
  - word-vector: Word-vector method for capturing traces, requires a pre-trained model.
  - llm-vector: Word-vector embeddings taken from openai.

- <options_> run options

  - rt:    requirement tree mode,
    - includes parent requirements for keyword extraction, requires a file named 'requirements.txt' in the root directory of the repository
          
  - rg:    reset graph, 
    - deletes the graph pickle to re-create the graph from scratch

---------

We have a Config file which controls everything related to running configurations. Beware that the tool needs the requirement specifications for the repository you provided. The two repositories with their requirements is available on the repo, which were also used for development of this tool.

### Dashboard

Navigate to http://neodash.graphapp.io/ to view the dashboard. From the menu, navigate to `new dashboard`. Provide the default neo4j credentials mentioned above. From left menu bar, navigate to `load`. Proceed to `Select from Neo4j` option on the opening page and select our pre-uploaded dashboard template. The dashboard must be ready for use. In the case that dashboard template doesn't show up, `Select from File` option can always be used and the dashboard template can be taken from our [repository](https://github.com/ersoykadir/Requirement-Traceability-Analysis/blob/main/dashboard-template.json). 
Navigate to http://localhost:7474/ to view graph database.

  
## Example queries for Neo4j graph database

The following query returns the traces for a specific requirement number.

```bash
MATCH p=(r)-[t:tracesTo]->(a) 
where r.number='<req_number>'
RETURN *
```

For keyword search, the following query returns the traces which have a specific keyword match.

```bash
MATCH p=(r)-[t:tracesTo]->(a) 
WHERE t.keyword='<keyword>'
RETURN *
```

The following query returns the traces between the requirement and the specific artifact type.

```bash
MATCH p=(r)-[t:tracesTo]->(a:<artifact_type>) 
where r.number='<req_number>'
RETURN *
```
  
