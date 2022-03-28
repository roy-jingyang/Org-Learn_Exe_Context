#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from copy import deepcopy

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold

from ordinor.io import read_disco_csv
from ordinor.execution_context import ODTMiner

# input log
fn_log = sys.argv[1]

el = read_disco_csv(fn_log)

# TODO: use only data from selected municipality
el = el[el['r:municipality'] == 'muni-5']

print(len(pd.unique(el['org:resource'])))
print(len(pd.unique(el['concept:name'])))


# specification

all_cand_attrs = [
    # WABO
    #{'attr': 'ct:channel', 'attr_type': 'categorical', 'attr_dim': 'CT'},
    #{'attr': 'tt:weekday', 'attr_type': 'categorical', 'attr_dim': 'TT'}, 
    #{'attr': 'tt:ampm', 'attr_type': 'categorical', 'attr_dim': 'TT'},
    
    # BPIC15
    {'attr': 'ct:permit_type', 'attr_type': 'categorical', 'attr_dim': 'CT'},
    {'attr': 'at:phase', 'attr_type': 'categorical', 'attr_dim': 'AT'},
    {'attr': 'tt:weekday', 'attr_type': 'categorical', 'attr_dim': 'TT'}, 
    {'attr': 'tt:ampm', 'attr_type': 'categorical', 'attr_dim': 'TT'},
    
    # BPIC17
    #{'attr': 'ct:loan_goal', 'attr_type': 'categorical', 'attr_dim': 'CT'},
    #{'attr': 'ct:application_type', 'attr_type': 'categorical', 'attr_dim': 'CT'},
    #{'attr': 'ct:requested_amount', 'attr_type': 'numeric', 'attr_dim': 'CT'},
    #{'attr': 'at:event_origin', 'attr_type': 'categorical', 'attr_dim': 'AT'},
    #{'attr': 'tt:weekday', 'attr_type': 'categorical', 'attr_dim': 'TT'}, 
    #{'attr': 'tt:ampm', 'attr_type': 'categorical', 'attr_dim': 'TT'},
]

spec = dict()
spec['cand_attrs'] = all_cand_attrs


# run algorithm

miner = ODTMiner(el, spec, eps=1e-2, trace_history=True)

