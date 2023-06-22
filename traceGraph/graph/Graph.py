import json
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
from trace_util.llm_vectors import get_embeddings_for_nodes

"""
    Class representing the graph of software artifacts.
"""
class Graph:
    def __init__(self):
        self.nodes = {}
        self.issue_nodes = build_issue_nodes()
        self.pr_nodes = build_pr_nodes()
        self.commit_nodes = build_commit_nodes()
        self.requirement_nodes = build_requirement_nodes()
        self.nodes = self.issue_nodes | self.pr_nodes | self.commit_nodes | self.requirement_nodes
        self.artifact_nodes = self.issue_nodes | self.pr_nodes | self.commit_nodes
        self.model = None

        self.lemmatize_and_remove_stopwords()
        self.create_model(Config().search_method)
        self.save_graph()

    # Save the graph to a pickle file
    def save_graph(self):	
        with open(f'./data_{Config().repo_name}/graph.pkl', 'wb') as f:	
            pickle.dump(self, f) 

    # Create the vector model for the graph
    def create_model(self, modeltype):
        
        # if Config().model_setup and Config().experiment_mode:
        #     # Experiment mode is on and model is already setup
        #     return
        
        print('Creating model...')

        total_tokens = 0
        # for node in self.nodes.values():
        #     total_tokens += len(node.tokens)
        # print('Total tokens:', total_tokens)    
        
        if modeltype == 'tf-idf':
            # Prepare the corpus
            corpus = {}
            for a in self.nodes.values():
                corpus[a.number] = a.text
            # Create the tf-idf vectors
            vectorizer = TfidfVectorizer(min_df=2)#min_df=2
            tfidf_vectors = vectorizer.fit_transform(corpus.values())
            self.tfidf_vectors = tfidf_vectors.toarray()
            index = 0
            print(tfidf_vectors.shape)
            for c in corpus.keys():
                a = self.nodes[c]
                # if a.node_type == 'requirement' and a.parent is not None and Config().parent_mode:
                #     # If parent mode is on, combine the artifact vector with the parent vector
                #     print("here")
                #     a.vector = a.parent.vector + self.tfidf_vectors[index]
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
        elif modeltype == 'llm-vector':
            # Get the embeddings for each node
            if not os.path.exists(f"data_{Config().repo_name}/embeddings.json"):
                get_embeddings_for_nodes(self)
            f = open(f"data_{Config().repo_name}/embeddings.json", "r")
            embeddings = json.loads(f.read())
            f.close()
            embeddings = embeddings['embeddings']
            for e in embeddings:
                number = e['number']
                number = int(number) if number.isdigit() else number
                self.nodes[number].vector = e['embedding']
        # self.save_graph()
        # Config().model_setup = True

    # Lemmatize and remove stopwords from each artifact in the graph
    def lemmatize_and_remove_stopwords(self):
        nodes = self.artifact_nodes if Config().search_method == 'keyword' else self.nodes
        for artifact in nodes.values():
            # artifact.text = remove_stopwords_from_text(artifact.text, "../keyword_extractors/SmartStopword.txt")
            # artifact.text = lemmatizer(artifact.text)
            artifact.preprocess_text()

    # Combine two trace tuples
    def combine(self, tuple1, tuple2):
        try:
            if Config().search_method == 'keyword':
                tuple1[0] = tuple1[0] + tuple2[0]
            else:
                # For now, similarity equals to max similarity when pr and commit traces are combined
                tuple1[0] = (tuple1[0] + tuple2[0]) / 2
            tuple1[1].extend(tuple2[1])
            tuple1[1] = list(set(tuple2[1]))
            return tuple1
        except Exception as e:
            print(str(e))
            print('pr_tuple:', tuple1)
            print('commit_tuple:', tuple2)
            raise e
    
    # Connect commit trace links over their related pull requests if they have one
    # This simplifies the graph and makes it easier to trace
    def connect_prs_from_commits(self):
        # Get commits that have associated prs
        for req in self.requirement_nodes.values():
            commits_to_delete = []
            for commit_number in req.commit_traces.keys():
                associated_pr = self.commit_nodes[commit_number].associatedPullRequest
                if associated_pr != None:
                    # Commit has an associated pr
                    # Connect its trace over the pr
                    if associated_pr in req.pr_traces.keys():
                        req.pr_traces[associated_pr] = self.combine(req.pr_traces[associated_pr], req.commit_traces[commit_number])
                    else:
                        req.pr_traces[associated_pr] = req.commit_traces[commit_number]
                    commits_to_delete.append(commit_number)
                else:
                    # Commit has no associated pr
                    pass
            # Delete the commit traces that have been combined with pr traces
            for commit_number in commits_to_delete:
                del req.commit_traces[commit_number]