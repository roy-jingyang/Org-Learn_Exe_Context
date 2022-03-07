#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from itertools import combinations

from scipy.spatial.distance import pdist
from scipy.stats import entropy
import pandas as pd

from ordinor.io import read_disco_csv
from ordinor import constants as const

fn_event_log = sys.argv[1]
method = sys.argv[2]
if len(sys.argv) > 3:
    is_syn_log = True if sys.argv[3] == 'syn' else False

def dispersal(rl, dims):
    # convert type names to codes (to apply pdist)
    rl = rl.astype('category')
    rl[const.CASE_TYPE] = rl[const.CASE_TYPE].cat.codes
    rl[const.ACTIVITY_TYPE] = rl[const.ACTIVITY_TYPE].cat.codes
    rl[const.TIME_TYPE] = rl[const.TIME_TYPE].cat.codes

    total_dispersal = 0

    n_events_total = len(rl)

    for r, events in rl.groupby(const.RESOURCE):
        n_events = len(events)
        wt =  n_events / n_events_total

        if n_events > 1:
            # 2 or more events
            avg_event_pdist = pdist(
                events[dims].to_numpy(), metric='hamming'
            ).mean()
        else:
            # only 1 event
            avg_event_pdist = 0
        
        total_dispersal += wt * avg_event_pdist

    return total_dispersal


def impurity(rl, dims):
    total_impurity = 0
    for em, events in rl.groupby(dims):
        wt = len(events) / len(rl)

        # calculate the discrete distribution
        pk = [
            len(r_events)  / len(events)
            for r, r_events in events.groupby(const.RESOURCE)
        ]
        if len(pk) > 1:
            # entropy
            total_impurity += wt * entropy(pk, base=2)
        else:
            total_impurity += 0

    return total_impurity

if __name__ == '__main__':
    # read event log as input
    if is_syn_log:
        el = pd.read_csv(fn_event_log, index_col='event_id')
    else:
        el = read_disco_csv(fn_event_log)
    print(el)

    if is_syn_log:
        ACT_ATTR_NAME = 'attr-1'
    else:
        # CT
        CASE_ATTR_NAME = 'ct:channel'
        #CASE_ATTR_NAME = 'ct:application_type'
        #CASE_ATTR_NAME = 'ct:permit_type'
    
        # AT
        ACT_ATTR_NAME = const.ACTIVITY
        #ACT_ATTR_NAME = 'at:event_origin'
    
        # TT
        def ampm(ts):
            return 'AM' if ts.hour < 12 else 'PM'
    

    # hand-make resource logs!
    rl = el[[const.RESOURCE]].copy()

    if method == 'null':
        # Null learning
        # All-in-One: lowest dispersal, highest impurity
        rl[const.CASE_TYPE]     = 'undefined'
        rl[const.ACTIVITY_TYPE] = 'undefined'
        rl[const.TIME_TYPE]     = 'undefined'
        dims = [const.ACTIVITY_TYPE]

    elif method == 'a':
        rl[const.CASE_TYPE]     = 'undefined'
        rl[const.ACTIVITY_TYPE] = el[ACT_ATTR_NAME].copy()
        rl[const.TIME_TYPE]     = 'undefined'
        dims = [const.ACTIVITY_TYPE]

    elif method == 'c':
        rl[const.CASE_TYPE]     = el[CASE_ATTR_NAME].copy()
        rl[const.ACTIVITY_TYPE] = 'undefined'
        rl[const.TIME_TYPE]     = 'undefined'
        dims = [const.CASE_TYPE]

    elif method == 't':
        rl[const.CASE_TYPE]     = 'undefined'
        rl[const.ACTIVITY_TYPE] = 'undefined'
        rl[const.TIME_TYPE]     = el[const.TIMESTAMP].apply(ampm).copy()
        dims = [const.TIME_TYPE]

    elif method == 'ca':
        rl[const.CASE_TYPE]     = el[CASE_ATTR_NAME].copy()
        rl[const.ACTIVITY_TYPE] = el[ACT_ATTR_NAME].copy()
        rl[const.TIME_TYPE]     = 'undefined'
        dims = [const.CASE_TYPE, const.ACTIVITY_TYPE]

    elif method == 'at':
        rl[const.CASE_TYPE]     = 'undefined'
        rl[const.ACTIVITY_TYPE] = el[ACT_ATTR_NAME].copy()
        rl[const.TIME_TYPE]     = el[const.TIMESTAMP].apply(ampm).copy()
        dims = [const.ACTIVITY_TYPE, const.TIME_TYPE]

    elif method == 'ct':
        rl[const.CASE_TYPE]     = el[CASE_ATTR_NAME].copy()
        rl[const.ACTIVITY_TYPE] = 'undefined'
        rl[const.TIME_TYPE]     = el[const.TIMESTAMP].apply(ampm).copy()
        dims = [const.CASE_TYPE, const.TIME_TYPE]

    elif method == 'cat':
        rl[const.CASE_TYPE]     = el[CASE_ATTR_NAME].copy()
        rl[const.ACTIVITY_TYPE] = el[ACT_ATTR_NAME].copy()
        rl[const.TIME_TYPE]     = el[const.TIMESTAMP].apply(ampm).copy()
        dims = [const.CASE_TYPE, const.ACTIVITY_TYPE, const.TIME_TYPE]

    elif method == 'enum':
        # Enumerating
        # One-for-Each: highest dispersal, lowest impurity
        rl[const.CASE_TYPE] = rl.index
        rl[const.ACTIVITY_TYPE] = rl.index
        rl[const.TIME_TYPE] = rl.index
        dims = [const.CASE_TYPE, const.ACTIVITY_TYPE, const.TIME_TYPE]

    else:
        raise NotImplementedError

    print(rl)
    print('-' * 80)
    print('{} Case Types, {} Activity types, {} Time types.'.format(
        len(pd.unique(rl[const.CASE_TYPE])),
        len(pd.unique(rl[const.ACTIVITY_TYPE])),
        len(pd.unique(rl[const.TIME_TYPE]))
    ))
    num_cubes = len(rl.groupby([
        const.CASE_TYPE,
        const.ACTIVITY_TYPE,
        const.TIME_TYPE
    ]).groups)
    print('Number of "cubes": {}'.format(num_cubes))
    
    val_dispersal = dispersal(rl, dims)
    val_impurity = impurity(rl, dims)

    print('dispersal\t= {:.6f}'.format(val_dispersal))
    print('impurity\t= {:.6f}'.format(val_impurity))

    print('{},{:.6f},{:.6f}'.format(num_cubes, val_dispersal, val_impurity))
