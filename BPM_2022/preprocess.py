import pandas as pd

# Load raw data & Preprocess DataFrame (enrich with derived attributes)
df = pd.read_csv('local/bpic15.csv')[[
    'Case ID', 'Activity', 'Resource', 'Complete Timestamp',
    '(case) parts', 'action_code'
]]
df = df.rename(columns={
    '(case) last_phase': 'ct:last_phase', 
    '(case) parts': 'case_parts'
})

# Derive case attributes
# user-specified categorization rule for attribute "case_parts"
df = df[~df['case_parts'].isna()]
df['case_parts_has_Bouw'] = df.apply(
    lambda row: 'Bouw' 
    if 'Bouw' in str(row['case_parts']).split(',') 
    else 'Non Bouw', axis=1
)

# Only look at the main subprocess: "01_HOOFD"
df = df[~df['action_code'].isna()]
df = df[df['action_code'].str.startswith('01_HOOFD')]
df['phase'] = df['action_code'].apply(lambda code: code[:10])

# Derive time-related attributes
df['Complete Timestamp'] = pd.to_datetime(df['Complete Timestamp'], format='ISO8601')
WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
df['weekday'] = df['Complete Timestamp'].apply(lambda ts: WEEKDAYS[ts.dayofweek])
df['ampm'] = df['Complete Timestamp'].apply(lambda ts: 'AM' if ts.hour < 12 else 'PM')

print(df[~df.isna()])
df.to_csv(f'bpic15.preprocessed.csv')
