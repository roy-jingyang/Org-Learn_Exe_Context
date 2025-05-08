import pandas as pd
# Load raw data & Preprocess DataFrame (enrich with derived attributes)
log = 'bpic17'

preprocess = True

if preprocess:
    fn = f'data/raw/{log}.csv'
else:
    fn = f'data/processed/{log}.csv'

if preprocess:
    if log == 'wabo':
        df = pd.read_csv(fn)[[
            'Case ID', 'Resource', 'Complete Timestamp',
            'org:group', 'group',
            'concept:name', 'responsible', 'department', 'channel'
        ]]

        df = df.rename(columns={
            # Resource-related
            'department': 'r:department',
            'org:group': 'r:org:group',
            'group': 'r:group',
            # CT-related
            'channel': 'ct:channel',
            # AT-related
            'concept:name': 'Activity',
        })
        
        # filter meaningless values
        #df = df[~df['r:org:group'].isin(['EMPTY'])]
        #df = df[~df['r:group'].isin([''])]

    if log == 'bpic17':
        df = pd.read_csv(fn)[[
            'Case ID', 'Activity', 'Resource', 'Complete Timestamp',
            'EventOrigin', 'LoanGoal', 'ApplicationType', 'RequestedAmount'
        ]]

        df = df.rename(columns={
            # Resource-related
            # CT-related
            'LoanGoal': 'ct:loan_goal', 
            'ApplicationType': 'ct:application_type', 
            'RequestedAmount': 'ct:requested_amount', 
            # AT-related
            'EventOrigin': 'at:event_origin'
        })
        
        # filter meaningless values
        #df = df[~df['ct:loan_goal'].isin(['Unknown'])]
        

    if log == 'bpic15':
        df = pd.read_csv(fn)[[
            'Case ID', 'Activity', 'Resource', 'Complete Timestamp',
            '(case) last_phase', '(case) parts', 'action_code', 'municipality'
        ]]
        df = df.rename(columns={
            # Resource-related
            'municipality': 'r:municipality',
            # CT-related
            '(case) last_phase': 'ct:last_phase', 
            # AT-related
        })
        df = df.rename(columns={
            '(case) parts': 'case_parts'
        })
        # TODO: derive 'ct:permit_type', 'at:phase'
        df = df[~df['case_parts'].isna()]
        df['ct:permit_type'] = df.apply(lambda row: 'Bouw' if 'Bouw' in str(row['case_parts']).split(',') else 'Non Bouw', axis=1)

        # only look at the main subprocess: "01_HOOFD"
        df = df[~df['action_code'].isna()]
        df = df[df['action_code'].str.startswith('01_HOOFD')]
        df['at:phase'] = df['action_code'].apply(lambda code: code[:10])
        
        # filter meaningless values

    if log == 'bpic18':
        pass

    # Universal (on Disco outputs)
    # derive and append TT related candidate attributes
    df['Complete Timestamp'] = pd.to_datetime(df['Complete Timestamp'], format='%Y-%m-%d %H:%M:%S.%f')
    MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    df['tt:month'] = df['Complete Timestamp'].apply(lambda ts: MONTHS[ts.month-1])
    df['tt:day'] = df['Complete Timestamp'].apply(lambda ts: 'Day_{}'.format(ts.day))
    WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    df['tt:weekday'] = df['Complete Timestamp'].apply(lambda ts: WEEKDAYS[ts.dayofweek])
    df['tt:ampm'] = df['Complete Timestamp'].apply(lambda ts: 'AM' if ts.hour < 12 else 'PM')
    
    print(df)
    df.to_csv(f'data/processed/{log}.csv')
else:
    df = pd.read_csv(fn, index_col=0)
    print(df)
