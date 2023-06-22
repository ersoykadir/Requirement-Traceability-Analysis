import json
import openai
import os
openai.api_key = os.environ.get('OPENAI_API_KEY')

max_tokens = 8191
tokens_per_request = 40000

from config import Config

from ratelimit import limits, RateLimitException, sleep_and_retry
import time

ONE_MINUTE = 60
MAX_CALLS_PER_MINUTE = 3

current_request = 0

@sleep_and_retry
@limits(calls=MAX_CALLS_PER_MINUTE, period=ONE_MINUTE)
def get_embeddings(sentences):
    # global current_request
    # if current_request > 3:
    #     time.sleep(60)
    #     current_request = 0
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=sentences,
    )
    # current_request += 1
    embeddings = response['data']
    return embeddings


import tiktoken
import pandas as pd

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def num_tokens_from_strings(strings: list[str], encoding_name: str) -> int:
    """Returns the number of tokens in a list of text strings."""
    return sum(num_tokens_from_string(s, encoding_name) for s in strings)

import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
# Preprocesses the text of the node.
def preprocess_text(text):
    text = text.lower()
    text = text.rstrip('\n')
    text = text.translate(str.maketrans('', '', string.digits))
    text = text.translate(str.maketrans('', '', string.punctuation))
    sw = stopwords.words('english')
    sw = []
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in sw]
    text = ' '.join(tokens)
    return text

import numpy as np
def get_embeddings_for_nodes(graph):
    global max_tokens, tokens_per_request

    # embeddings_df = pd.DataFrame(columns=['number', 'node_type', 'embedding'])
    embeddings = []
    batch = []
    tokens = 0

    # Save at each 5 requests
    requests = 0
    for node in graph.nodes.values():
        print("Node {}".format(node.number) )
        # dict = {'number': node.number, 'node_type': node.node_type, 'embedding': None}
        # text = preprocess_text(node.text)
        text = node.text
        node_tokens = num_tokens_from_string(text, "cl100k_base")
        if node_tokens > max_tokens:
            print("Node {} has # tokens: {}".format(node.number, node_tokens))
            text = text[:max_tokens]
        if node_tokens == 0:
            continue
        tokens += node_tokens
        print("Tokens: {}".format(tokens))
        if tokens > tokens_per_request:
            # make request
            batch = np.array(batch)
            response = get_embeddings(list(batch[:,2]))
            # add the embeddings to the dict           
            for i, res in enumerate(response):
                # embeddings_df.loc[len(embeddings_df)] = [batch[i,0], batch[i,1], res['embedding']]
                dict = {'number': batch[i,0], 'node_type': batch[i,1], 'embedding': res['embedding']}
                embeddings.append(dict)
            # reset tokens and batch
            tokens = 0
            batch = []
            # add the current node to the batch
            batch.append([node.number, node.node_type, text])
            tokens += node_tokens

            # embeddings_df.to_csv('embeddings.csv', mode='a', index=False, header=False, sep=';')
            # embeddings_df = pd.DataFrame(columns=['number', 'node_type', 'embedding'])
        else:
            batch.append([node.number, node.node_type, text])

    if tokens > 0:
        batch = np.array(batch)
        response = get_embeddings(list(batch[:,2]))
        # add the embeddings to the dict           
        for i, res in enumerate(response):
            # embeddings_df.loc[len(embeddings_df)] = [batch[i,0], batch[i,1], res['embedding']]
            dict = {'number': batch[i,0], 'node_type': batch[i,1], 'embedding': res['embedding']}
            embeddings.append(dict)
        # reset tokens and batch
        tokens = 0
        batch = []
        # add the current node to the batch
        batch.append([node.number, node.node_type, text])
        tokens += node_tokens

        # embeddings_df.to_csv('embeddings.csv', mode='a', index=False, header=False, sep=';')
        # embeddings_df = pd.DataFrame(columns=['number', 'node_type', 'embedding'])

    f = open(f"data_{Config().repo_name}/embeddings.json", "w")
    dump = {'embeddings': embeddings}
    f.write(json.dumps(dump))
    f.close()

# from graph.Graph import Graph

# graph = Graph()
# print("Graph loaded")
# get_embeddings_for_nodes(graph)

"""
{
    "embeddings": [
        {
            "number": 1,
            "node_type": "class",
            "embedding": []
        },
        {
            "embedding": []
        }
}
"""

def read_embeddings():
    # embeddings_df = pd.read_csv('embeddings.csv', sep=';')
    # print(embeddings_df.iloc[1])
    # number, node_type, embedding = embeddings_df.iloc[1]
    # embedding = embedding[1:-1].split(',')
    # print(embedding[0])
    f = open("embeddings.json", "r")
    embeddings = json.loads(f.read())
    f.close()
    embeddings = embeddings['embeddings']
    return embeddings

# read_embeddings()