from trace_util.trace import trace
from graph.Graph import Graph
from config import Config

filter_thresholds = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4,
                     0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.77, 0.78, 0.79, 0.8]
search_methods = ['tf-idf', 'word-vector', 'llm-vector', 'keyword']
parent_mode = False
reset_graph = False
Config()
Config().parent_mode = parent_mode
Config().reset_graph = reset_graph
Config().experiment_mode = True

def experiment():
    for search_method in search_methods:
        Config().search_method = search_method
        graph = Graph()
        if search_method == 'keyword':
            Config().filter_threshold = 0
            trace(graph)
            print("Keyword search is done!")
        else:
            for filter_threshold in filter_thresholds:
                Config().filter_threshold = filter_threshold
                trace(graph)
                print("Filter threshold: ", filter_threshold, " is done for", search_method, "!")
        print(search_method, " is done!")
    
    average_recall_and_precision()

import os, pandas

def average_recall_and_precision():

    res_path = f'./results/{Config().repo_name}/'
    results = os.listdir(res_path)

    # initialize dictionary
    res_dict = {}
    keyword_res = []
    
    # iterating through the elements of list
    for i in filter_thresholds:
        res_dict[i] = {
            'tf-idf': [],
            'word-vector': [],
            'llm-vector': [],
        }

    for result in results:
        if result.endswith('.csv'):
            df = pandas.read_csv(res_path+result)
            res = result.split('.csv')[0]
            recall_avg = "{:.3f}".format(df['Recall'].mean())
            precision_avg = "{:.3f}".format(df['Precision'].mean())
            if 'keyword' in res:
                print(f'{result}: recall: {recall_avg}, precision: {precision_avg}')
                keyword_res = [recall_avg, precision_avg]
                continue
            method, _, filter_threshold = res.split('_')
            filter_threshold = float(filter_threshold)
            res_dict[filter_threshold][method] = [recall_avg, precision_avg]
            print(f'{result}: recall: {recall_avg}, precision: {precision_avg}')

    result_table(res_dict, keyword_res)

def result_table(dict, keyword_res):
    f = open('result_table','w')
    f.write('keyword:'+str(keyword_res[0]) + str(keyword_res[1]))
    f.write('\n')
    for th in dict:
        methods = dict[th]
        text = str(th) + ' & ' + methods['tf-idf'][0] + ' & ' + methods['tf-idf'][1] + ' & ' + methods['word-vector'][0] + ' & ' + methods['word-vector'][1] + ' & ' + methods['llm-vector'][0] + ' & ' + methods['llm-vector'][1] + '\n'
        f.write(text)
    f.close()
if __name__ == "__main__":
    experiment()