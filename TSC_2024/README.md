Paper titled "Discovering Work Specialization through Process Mining",
submitted, under review.

Please use the following list to find the resources related to this paper:

* For implementation of the proposed algorithm for learning execution contexts
  from an event log, check out the source code of the latest [OrdinoR
  library](https://pypi.org/project/ordinor/), specifically, the `SASearchMiner`
  class in module `ordinor.execution_context.rule_based.search`. 
  Note that the same module also provides the implementations of the tree-based
  algorithm as a baseline in the evaluation experiments.
* For the source code used in the evaluation experiments (Section 5 in the
  paper), check out the **experiments/** folder for Jupyter Notebooks (named as
  `[Logname]_preprocess.ipynb`), which implement the event log preprocessing steps;
  and the Python scripts (named as `[Logname]_ODT.py` and
  `[Logname]_search.py`), which implement the application of the tree-based and
  SA-based algorithms on different event logs.
* For the source code used in the case study analysis (Section 6 in the paper),
  check out the **case_study/** folder for the Jupyter Notebook
  (`bpic2015_case_study.ipynb`) implementing the analysis steps and showing the
  results. 

In addition, we attempted to implement a related algorithm in the SOTA (Van
Hulzen et al. 2021). The algorithm targets a different problem but may be
adapted for learning execution contexts. The implementations of that algorithm
can be found as R scripts under the **experiments/** folder as
`[Logname]_fmm.R`. We also tested the implemented SOTA algorithm as an extended
analysis in the revision of our paper. 
For details of this extended analysis and its results, please check out the
**experiments/results/Extended** folder, specifically, the PDF document
**Extended investigation on SOTA (Van Hulzen et al. 2021).pdf**.
