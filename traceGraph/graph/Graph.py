import sys, os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models import Word2Vec as w2v
from nltk.corpus import stopwords
sys.path.append('..')

from keyword_extractor.custom_extractor import lemmatizer, remove_stopwords_from_text
from .node_parser import build_issue_nodes, build_pr_nodes, build_commit_nodes, build_requirement_nodes


# Class representing the graph of software artifacts.
class Graph:
    def __init__(self, repo_number, parent_mode):
        # if repo_number == 2:
        #     self.issue_number_threshold = 309 # for group 2
        # elif repo_number == 3:
        #     self.issue_number_threshold = 258 # for group 3
        # else:
        #     raise Exception("Invalid repo number")
        self.repo_number = repo_number	
        self.nodes = {}
        self.issue_nodes = build_issue_nodes(repo_number)
        self.pr_nodes = build_pr_nodes(repo_number)
        self.commit_nodes = build_commit_nodes(repo_number)
        self.requirement_nodes = build_requirement_nodes(repo_number, parent_mode)
        self.nodes = self.issue_nodes | self.pr_nodes | self.commit_nodes | self.requirement_nodes
        self.artifact_nodes = self.issue_nodes | self.pr_nodes | self.commit_nodes

        self.lemmatize_and_remove_stopwords()
        self.save_graph()

    def save_graph(self):	
        with open(f'./data_group{self.repo_number}/graph.pkl', 'wb') as f:	
            pickle.dump(self, f) 

    def __str__(self):
        return f"Graph with {len(self.issue_nodes)} nodes."

    def create_model(self, modeltype):
        if modeltype == 'tfidf':
            corpus = {}
            for a in self.nodes.values():
                corpus[a.number] = a.text
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_vectors = vectorizer.fit_transform(corpus.values())
            self.tfidf_vectors = tfidf_vectors.toarray()
            index = 0
            for c in corpus.keys():
                a = self.nodes[c]
                a.vector = self.tfidf_vectors[index]
                index += 1

        elif modeltype == 'w2v':
            texts = []
            total_tokens = 0

            # Get the tokens of each node for training the w2v model
            for node in self.nodes.values():
                node.preprocess_text()
                texts.append(node.tokens)
                total_tokens += len(node.tokens)
            
            # Train the w2v model
            self.model = w2v(
                texts,
                min_count=3,  
                sg = 1,       
                window=7      
            )
            # Create the word vectors for each node
            total_missing_tokens = 0
            for node in self.nodes.values():
                total_missing_tokens += node.create_vector(self.model)
            print('Total missing tokens:', total_missing_tokens)
            print('Total tokens:', total_tokens)

    # Lemmatize and remove stopwords from the artifact
    def lemmatize_remove(self, artifact):
        artifact.text = remove_stopwords_from_text(artifact.text, "../keyword_extractors/SmartStopword.txt")
        artifact.text = lemmatizer(artifact.text)

    # Lemmatize and remove stopwords from each artifact in the graph
    def lemmatize_and_remove_stopwords(self):
        for artifact in self.artifact_nodes.values():
            artifact.text = remove_stopwords_from_text(artifact.text, "../keyword_extractors/SmartStopword.txt")
            artifact.text = lemmatizer(artifact.text)

    def combine(self, tuple1, tuple2):
        try:
            tuple1[0] = tuple1[0] + tuple2[0]
            tuple1[1].extend(tuple2[1])
            tuple1[1] = list(set(tuple2[1]))
            return tuple1
        except Exception as e:
            print(str(e))
            print('pr_tuple:', tuple1)
            print('commit_tuple:', tuple2)
            raise e
    
    def connect_prs_from_commits(self):
        # Get commits that have associated prs
        for req in self.requirement_nodes.values():
            commits_to_delete = []
            print(req.commit_traces.keys())
            for commit_number in req.commit_traces.keys():
                associated_pr = self.commit_nodes[commit_number].associatedPullRequest
                if associated_pr != None:
                    # combine data with req_to_pr
                    if associated_pr in req.pr_traces.keys():
                        req.pr_traces[associated_pr] = self.combine(req.pr_traces[associated_pr], req.commit_traces[commit_number])
                    else:
                        req.pr_traces[associated_pr] = req.commit_traces[commit_number]
                    commits_to_delete.append(commit_number)
                else:
                    pass
        
            for commit_number in commits_to_delete:
                if commit_number in req.commit_traces.keys():
                    del req.commit_traces[commit_number]
            
            print(req.commit_traces.keys())