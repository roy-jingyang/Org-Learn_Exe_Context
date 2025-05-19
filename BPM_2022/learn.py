#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from copy import deepcopy

import numpy as np
import pandas as pd

from ordinor.io import read_disco_csv
from ordinor.execution_context import ODTMiner

# Read input log
fn_log = 'bpic15.preprocessed.csv'
# Rename columns by XES standard for subsequent processing
el = pd.read_csv(fn_log).rename(columns={
    'Case ID': 'case:concept:name',
    'Activity': 'concept:name',
    'Resource': 'org:resource',
    'Complete Timestamp': 'time:timestamp'
})
print(el)

# Define attribute specification
spec = {
    'type_def_attrs': {
        # BPIC15
        'case_parts_has_Bouw': {'attr_type': 'categorical', 'attr_dim': 'CT'},
        'phase': {'attr_type': 'categorical', 'attr_dim': 'AT'},
        'weekday': {'attr_type': 'categorical', 'attr_dim': 'TT'}, 
        'ampm': {'attr_type': 'categorical', 'attr_dim': 'TT'},
    }
}

# Run learning algorithm
miner = ODTMiner(el, spec, max_height=12, trace_history=True)

# Label events by learning result
rl = miner.derive_resource_log(el)
for t in ['case_type', 'activity_type', 'time_type']:
    el[t] = rl[t]
# Merge type labels to create execution context labels
el['CO'] = el[['case_type', 'activity_type', 'time_type']].agg('-'.join, axis=1)
print(el)
el.to_csv('bpic15.preprocessed.labeled.csv')
