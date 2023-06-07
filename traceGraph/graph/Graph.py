import string
import sys, os
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models import Word2Vec as w2v
from gensim.models import KeyedVectors
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
wnet_lemmatizer = WordNetLemmatizer()
sys.path.append('..')

from keyword_extractor.custom_extractor import lemmatizer, remove_stopwords_from_text
from .node_parser import build_issue_nodes, build_pr_nodes, build_commit_nodes, build_requirement_nodes

from config import Config

# Class representing the graph of software artifacts.
class Graph:
    def __init__(self):
        self.nodes = {}
        self.issue_nodes = build_issue_nodes()
        self.pr_nodes = build_pr_nodes()
        self.commit_nodes = build_commit_nodes()
        self.requirement_nodes = build_requirement_nodes()
        self.nodes = self.issue_nodes | self.pr_nodes | self.commit_nodes | self.requirement_nodes
        self.artifact_nodes = self.issue_nodes | self.pr_nodes | self.commit_nodes

        self.lemmatize_and_remove_stopwords()
        self.save_graph()

    def save_graph(self):	
        with open(f'./data_{Config().repo_name}/graph.pkl', 'wb') as f:	
            pickle.dump(self, f) 

    def __str__(self):
        return f"Graph with {len(self.issue_nodes)} nodes."

    def create_model(self, modeltype):

        total_tokens = 0

        for node in self.nodes.values():
            total_tokens += len(node.tokens)
            
        if modeltype == 'tf-idf':
            corpus = {}
            for a in self.nodes.values():
                corpus[a.number] = a.text
            vectorizer = TfidfVectorizer(min_df=5)
            tfidf_vectors = vectorizer.fit_transform(corpus.values())
            self.tfidf_vectors = tfidf_vectors.toarray()
            index = 0
            for c in corpus.keys():
                a = self.nodes[c]
                a.vector = self.tfidf_vectors[index]
                index += 1

        elif modeltype == 'word-vector':

            # Get the pretrained model
            self.model = KeyedVectors.load_word2vec_format(Config().pretrained_model_path, binary=True) #load the model

            # Create the word vectors for each node
            total_missing_tokens = 0
            for node in self.nodes.values():
                total_missing_tokens += node.create_vector(self.model)
            print('Total missing tokens:', total_missing_tokens)
            print('Total tokens:', total_tokens)

    # Lemmatize and remove stopwords from each artifact in the graph
    def lemmatize_and_remove_stopwords(self):
        nodes = self.artifact_nodes if Config().search_method == 'keyword' else self.nodes
        for artifact in nodes.values():
            # artifact.text = remove_stopwords_from_text(artifact.text, "../keyword_extractors/SmartStopword.txt")
            # artifact.text = lemmatizer(artifact.text)
            artifact.preprocess_text()

    def combine(self, tuple1, tuple2):
        try:
            if Config().search_method == 'keyword':
                tuple1[0] = tuple1[0] + tuple2[0]
            else:
                tuple1[0] = max(tuple1[0], tuple2[0]) / 2 # For now, similarity equals to max similarity when both pr and commit has traces
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
                del req.commit_traces[commit_number]