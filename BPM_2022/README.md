Paper published in the BPM 2022 conference proceedings. 

Cite as: Yang, J.,
Ouyang, C., ter Hofstede, A. H. M., & van der Aalst, W. M. P. (2022). **No Time
to Dice: Learning Execution Contexts from Event Logs for
Resource-Oriented Process Mining.** In C. Di Ciccio, R. M. Dijkman, A.
del-Río-Ortega, & S. Rinderle-Ma (Eds.), Business Process Management - 20th
International Conference, BPM 2022, Münster, Germany, September 11-16, 2022,
Proceedings. (pp. 163–180). Springer.

NOTE: This README file is created after the publication of the paper. However,
the algorithm presented in the paper was not modifiled in any way other than
being released as part of the OrdinoR package. 

# Prerequisites
Install OrdinoR (version 0.2.1). Please find the instruction in the
[documentation](https://ordinor.readthedocs.io/en/latest/install.html).

# Dataset
The merged BPIC-15 log is used.

# Data Preprocessing
The following preprocessing steps are done on the merged BPIC-15 log:

* Derive a case attribute `case_parts_has_Bouw`. This correspondings to the
  user-specified categorization rules on attribute `case_parts`, described in
  Section 6.1 of the paper.
* Derive an event attribute `phase` by extracting phase information from the
  action code.
* Derive event attributes `weekday` and `ampm` by extracting the datetime
  information from the complete timestamps.

These are implemented in the file `preprocess.py`. A pre-processed CSV file as
result is stored as `bpic15.preprocessed.csv`.

# Applying the ODT algorithm to learn execution contexts
`python learn.py`

This uses the pre-processed CSV file (`bpic15.preprocessed.csv`) as input and
generates three files: 

* `ODTMiner[...]_solutions.out`: This file contains the step-wise tree node and
  categorization rule values during the learning procedure.
* `ODTMiner[...]_stats.out`: This file contains the step-wise dispersal and
  impurity values during the learning procedure.
* `bpic15.preprocessed.labeled.csv`: This file is the original input,
  pre-processed event log but with each event labeled by their corresponding
  case type, activity type, and time type of the execution context. 

Note that in the labeled CSV, the case types, activity type, time types, and
execution contexts are integer labels. To inteprete their meanings in terms of
the categorization rules, search for those integer labels in the
`ODTMiner[...]_solutions.out` file to find the categorization rules. For example:

* "AT.1862" can be interpreted by a line "AT=[1862](`phase` ∈
  {np.str_('01_HOOFD_0'), np.str_('01_HOOFD_1'), np.str_('01_HOOFD_4'),
  np.str_('01_HOOFD_5')})", which states that the this type name (AT.1682)
  corresponds to a rule that categorizes activities within the four phases (0,
  1, 4, 5) into the same activity type.
* "TT.546" can be interpreted by a line "TT=[546](`weekday` ∈
  {np.str_('Sat')})", which states that this type name (TT.546) corresponds to a
  rule that categorizes timestamps on Saturdays into one time type.

The actual integers in any run of the algorithm may differ. However, the final
results replicate the ones reported in Section 6.2 of the paper.

To help with the use of the learned execution contexts, we provide a CSV file
`bpic15.preprocessed.labeled.mapped.csv`, in which we mapped the integer labels
onto some string values representing the categorization rules. This CSV file is
used in the following application.

# Applying the learned execution contexts

These are implemented through the two Jupyter notebooks. Both use the labeled
and mapped event log file (`bpic15.preprocessed.labeled.mapped.csv`) as input:

* `apply-omm.ipynb`: This corresponds to the "Resource Profile Analysis"
  part in Section 6.3 of the paper.

* `apply-omm.ipynb`: This corresponds to the "Organizational Model Discovery"
  part in Section 6.3 of the paper.
