from main import main
from config import Config

filter_thresholds = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4,
                     0.45, 0.5, 0.55, 0.6, 0.65, 0.7]
search_methods = ['tf-idf', 'word-vector', 'keyword']
def experiment():
    for search_method in search_methods:
        parent_mode = False
        reset_graph = False
        Config()
        Config.search_method = search_method
        Config.parent_mode = parent_mode
        Config.reset_graph = reset_graph
        for filter_threshold in filter_thresholds:
            Config.filter_threshold = filter_threshold
            main()
            print("Filter threshold: ", filter_threshold, " is done!")

if __name__ == "__main__":
    experiment()