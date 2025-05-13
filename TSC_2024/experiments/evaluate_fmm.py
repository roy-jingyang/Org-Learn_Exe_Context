import sys
import pandas as pd

import ordinor.constants as const

from _search_algo_utils import evaluate_ec

def check_event_number_per_cluster(df, col_cluster):
    # this is determined as at least 5% of all events 
    # see Section 4.1 in Van Hulzen et al. 2021
    min_event_number = int(len(df) * 0.05)
    for cluster, events in df.groupby(col_cluster):
        if len(events) < min_event_number:
            return False
    return True

def convert_clustering_to_rl(df, col_res, col_cluster):
    rl = df[[col_res, col_cluster]].copy()
    rl[const.RESOURCE] = df[col_res]
    rl[const.CASE_TYPE] = rl[col_cluster].apply(lambda x: f'CT.{x}')
    rl[const.ACTIVITY_TYPE] = rl[col_cluster].apply(lambda x: f'AT.{x}')
    rl[const.TIME_TYPE] = rl[col_cluster].apply(lambda x: f'TT.{x}')
    return rl

if __name__ == '__main__':
    fn = sys.argv[1]
    df = pd.read_csv(fn)
    results = []
    for i in range(1, 21):
        if (
            f'ClusterRep_{i}' in df.columns
            and
            check_event_number_per_cluster(
                df, col_cluster=f'ClusterRep_{i}'
            )
        ):
            rl = convert_clustering_to_rl(
                df, col_res='Resource', col_cluster=f'ClusterRep_{i}'
            )
            dis, imp = evaluate_ec(rl)
            results.append({
                'iteration': i,
                'impurity': imp,
                'dispersal': dis,
                'note': '',
            })
        else:
            results.append({
                'iteration': i,
                'impurity': pd.NA,
                'dispersal': pd.NA,
                'note': 'Invalid due to invalid log-likelihood or undersized clusters'
            })
    results = pd.DataFrame(results)
    results['score_HMean'] = (
        2 * (1 - results['impurity']) * (1 - results['dispersal'])
        /
        ((1 - results['impurity']) + (1 - results['dispersal']))
    )
    print(results)
