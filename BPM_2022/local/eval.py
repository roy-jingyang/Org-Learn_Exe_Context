#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from itertools import combinations

from scipy.spatial.distance import pdist
from scipy.stats import entropy
import pandas as pd

from ordinor.io import read_disco_csv
from ordinor import constants as const

fn_res_log = sys.argv[1]

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
    max_impurity = entropy(
        rl[const.RESOURCE].value_counts(normalize=True),
        base=2
    )

    return total_impurity / max_impurity

if __name__ == '__main__':
    dims = ['case_type', 'time_type']
    # read resource log as input
    rl = pd.read_csv(fn_res_log)

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
    for cube, events in rl.groupby([
        const.CASE_TYPE,
        const.ACTIVITY_TYPE,
        const.TIME_TYPE
    ]):
        print(cube)
        print('\t', end='')
        print(f"{len(events)} events")
    
    val_dispersal = dispersal(rl, dims)
    val_impurity = impurity(rl, dims)

    print('dispersal\t= {:.6f}'.format(val_dispersal))
    print('impurity\t= {:.6f}'.format(val_impurity))

    print('{},{:.6f},{:.6f}'.format(num_cubes, val_dispersal, val_impurity))

