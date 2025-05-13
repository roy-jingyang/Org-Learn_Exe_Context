import pandas as pd

import ordinor.constants as const
from ordinor.execution_context.rule_based import dispersal, impurity
from ordinor.io import read_csv

def evaluate_ec(rl):
    COLS = [const.CASE_TYPE, const.ACTIVITY_TYPE, const.TIME_TYPE]
    # m_event_co : pandas.Series
    #     An array indexed by event ids, recording labels of the execution
    #     contexts to which the events belong to.
    mat_event_co = rl[COLS]
    for col in COLS:
        codes, _ = pd.factorize(mat_event_co[col])
        mat_event_co.loc[:, col] = codes.astype(str)
    mat_event_co.loc[:, '_co'] = mat_event_co[COLS].agg('-'.join, axis=1)
    mat_event_co.loc[:, '_co'], _ = pd.factorize(mat_event_co['_co'])
    m_event_co = mat_event_co['_co']
    # m_co_t : pandas.DataFrame
    #     An array indexed by execution context ids, recording labels of
    #     the case types, activity types, and time types of execution
    #     contexts, i.e., the column number is 3.
    m_co_t = mat_event_co.drop_duplicates(subset='_co')
    m_co_t = m_co_t.set_index('_co')
    m_co_t = m_co_t.astype(int)
    print('# execution contexts: {}'.format(len(m_co_t)))
    # m_event_r : pandas.Series
    #     An array indexed by event ids, recording ids of the resources who
    #     originated the events.
    m_event_r = rl[const.RESOURCE]
    imp = impurity(m_event_co, m_event_r)
    dis = dispersal(m_co_t, m_event_co, m_event_r)
    print('Dispersal:\t{:.6f}'.format(dis))
    print('Impurity:\t{:.6f}'.format(imp))
    return dis, imp

def print_log_stats(log, spec):
    print('#events:\t{}'.format(len(log)))
    print('#cases:\t{}'.format(log[const.CASE_ID].nunique()))
    print('#res.:\t{}'.format(log[const.RESOURCE].nunique()))
    tds = list(spec['type_def_attrs'].keys())
    n_tds = len(tds)
    n_td_vals = 0
    ncomb_td_vals_all = 1
    for attr in tds:
        n_td_vals += log[attr].nunique()
        ncomb_td_vals_all *= log[attr].nunique()
    ncomb_td_vals_observed = len(log.drop_duplicates(subset=tds))
    print('#res-events:\t{}'.format(
        len(log.dropna(subset=tds+[const.RESOURCE]))
        ))
    print('#td.:\t{}'.format(n_tds))
    print('#tdv.:\t{}'.format(n_td_vals))
    print('#NC tdv. all:\t{}'.format(ncomb_td_vals_all))
    print('#NC tdv. observed:\t{}'.format(ncomb_td_vals_observed))

def print_collated_results(miner, dis, imp):
    num_execution_context = len(miner._nodes)
    num_ct, num_at, num_tt = 0, 0, 0
    for t, rules in miner.type_dict.items():
        if t.startswith('CT'):
            num_ct += 1
        elif t.startswith('AT'):
            num_at += 1
        elif t.startswith('TT'):
            num_tt += 1
        else:
            raise ValueError('Unknown types in miner.type_dict')
    print('Collated_result,{},{},{},{},{:.6f},{:.6f}'.format(
        num_execution_context, num_ct, num_at, num_tt,
        dis, imp
    ))

