
# Requirement Traceability Tool

This project creates a graph structure that contains software artifact nodes and their traces to each other. 



## Used Technologies

**Programming Language:** Python

**Graph DB:** Neo4j

  
## Authors

- [Ecenur Sezer](https://www.github.com/codingAku)
- [Kadir Ersoy](https://www.github.com/ersoykadir) 


  
## How to Run

The project needs Python=3.10.0 to operate. 

You can download it by clicking [here](https://www.python.org/downloads/release/python-3100/).

--------
First create a virtual environment on Python using _venv_ library.

```bash
  python -m venv c:\path\to\myenv
```
--------

Activate the environment based on your operating system and the shell.

-----

for POSIX:

- bash/zsh
```bash
source <venv>/bin/activate
```

- fish
```bash
source <venv>/bin/activate.fish
```
- csh/tcsh
```bash
source <venv>/bin/activate.csh
```
- PowerShell
```bash
<venv>/bin/Activate.ps1
```
for Windows:

- cmd.exe
```bash
<venv>\Scripts\activate.bat
```
- PowerShell
```bash
<venv>\Scripts\Activate.ps1
```
------
Clone the project using the following shell command.

```bash
  git clone https://github.com/ersoykadir/Requirement-Traceability-Analysis.git
```

Navigate to the root directory of the project and install the required dependencies.

```bash
  pip install -r requirements.txt
```

Navigate to the root directory of the project and run Docker to activate Neo4j server.

```bash
  docker-compose up -d
```
Create a _.env_ file with the following content:
 
```bash
GITHUB_USERNAME=<your github username>
GITHUB_TOKEN=<your github token>
NEO4J_PASSWORD="password"
```
You can find a file named _.env.example_ as a template in the root directory.

Navigate to the traceGraph directory under the root.
```bash
cd ./traceGraph
```

Run _.main.py_ with two system arguments; 

```bash
python ./main.py <repo_number> <search_method>
```

- <repo_number> indicates the number of github repositories on Bounswe 2022, setting it 2 will create traces for Learnify and 3 is for BUcademy.

- <search_method> indicates the method used for searching traces, it could be either "keyword" or "word-vector".

---------

Navigate to http://localhost:7474/ to view results on neo4j.


  
## Examples for Neo4j

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
  
