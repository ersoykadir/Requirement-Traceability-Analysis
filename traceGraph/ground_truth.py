# Ground truth values
ground_truth = {
    "1.1.1.4.2": {
        'issues': [957, 955, 678, 530, 521, 498, 489, 481, 464, 454, 453, 449, 444, 434, 429, 418, 417, 406, 395, 385, 384, 383, 379, 375, 364, 337, 331, 325, 323, 322],
        'prs': [537, 523, 463, 455, 458, 450, 445, 442, 435, 433, 431, 432, 420, 419, 411, 416, 392, 382, 374]
    },
    "1.1.2.14.2": {
        'issues': [957, 918, 823, 813, 812, 810, 782, 678, 614, 610, 609, 604, 579, 560, 546, 545, 517, 498, 347, 345, 341, 323],
        'prs': [922, 825, 816, 811, 809, 613, 582, 539, 550, 547]
    },
    "1.1.2.2": {
        'issues': [957, 955, 877, 867, 837, 797, 775, 491, 345, 325, 323, 322],
        'prs': [923, 915, 879, 843, 841, 835, 820, 783]
    },
    "1.1.1.2.1":{
        'issues': [331, 345, 380, 399, 439, 440, 491, 955, 957, 485, 467, 466, 447, 446, 444, 441, 422, 421, 419, 398, 396, 390, 382, 380, 337, 530, 537],
        'prs': []
    },
    '1.1.3.2.5.1':{
        'issues': [330, 343, 345, 583, 592, 750, 751, 752, 753, 754, 756, 757, 772, 773, 780, 787, 788, 793, 794, 827, 842, 847, 848, 860, 869, 872, 873, 880, 887, 892, 897, 955, 957],
        'prs': []
    },
    '1.1.3.2.6.1':{
        'issues':[330, 334, 341, 343, 344, 620, 622, 720],
        'prs': []
    },
    '1.1.2.14.1':{
        'issues': [560, 578, 579, 581, 582, 607, 613, 614, 651, 658, 718, 955, 505, 517, 538, 539, 545, 547, 550, 650, 658, 526, 577, 588, 595, 594, 596, 597, 606, 608, 609, 610, 612, 653, 662, 674, 675, 719, 720, 734, 765, 770, 781, 785, 786, 803, 812, 818, 825, 918, 922, 952, 955, 957],
        'prs': []
    },
    '1.1.2.15.1':{
        'issues': [397, 400, 657, 783, 957, 771, 851, 955, 915, 899, 898, 884, 879, 854],
        'prs': []
    }
}
import pandas as pd
from config import Config
def recall_and_precision(graph):
    global ground_truth
    fname = "./results/Recall_and_Precision" + Config().search_method
    if Config().search_method != "keyword":
        fname += "_" + str(Config().filter_threshold)
    data = []
    for req_number in ground_truth.keys():
        req = graph.requirement_nodes[req_number]

        actual = len(ground_truth[req_number]['issues']) + len(ground_truth[req_number]['prs'])

        total_captured = len(req.issue_traces) + len(req.pr_traces)
        if total_captured == 0:
            print("No traces captured for " + req_number)
        count = 0
        truth = ground_truth[req_number]['issues'] + ground_truth[req_number]['prs']
        for a in truth:
            if a in req.issue_traces.keys() or a in req.pr_traces.keys():
                count += 1
                
        if actual == 0:
            recall = 0
        else:
            recall = count/actual
        if total_captured == 0:
            precision = 0
        else:
            precision = count/total_captured

        data.append([req_number, actual, total_captured, count, recall, precision])
    
    df = pd.DataFrame(data, columns=['Requirement', 'Actual', 'Captured', 'True Captured', 'Recall', 'Precision'])
    df.to_csv(f'{fname}.csv', index=False)