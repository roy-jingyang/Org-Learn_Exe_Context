#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from copy import deepcopy

import numpy as np
import pandas as pd

from ordinor.io import read_csv
from ordinor import constants as const
from ordinor.execution_context import ODTMiner

# input log
fn_log = sys.argv[1]

el = read_csv(fn_log)
print('|R| =\t{}'.format(el[const.RESOURCE].nunique()))

print(el)

# set attribute specification
spec = {
    'type_def_attrs': {
        'attr-1': {'attr_type': 'categorical', 'attr_dim': 'AT'},
        'attr-2': {'attr_type': 'categorical', 'attr_dim': 'AT'},
        'attr-3': {'attr_type': 'categorical', 'attr_dim': 'AT'},
        'attr-4': {'attr_type': 'categorical', 'attr_dim': 'AT'},
        'attr-5': {'attr_type': 'categorical', 'attr_dim': 'AT'},
        'attr-6': {'attr_type': 'categorical', 'attr_dim': 'AT'},
        'attr-7': {'attr_type': 'categorical', 'attr_dim': 'AT'},
        'attr-8': {'attr_type': 'categorical', 'attr_dim': 'AT'},
        'attr-9': {'attr_type': 'categorical', 'attr_dim': 'AT'},
        'attr-10': {'attr_type': 'categorical', 'attr_dim': 'AT'},
    }
}

# run algorithm
miner = ODTMiner(el, spec, max_height=5, trace_history=False)

