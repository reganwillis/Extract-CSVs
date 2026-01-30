import os
import json
import pandas as pd

master_df = pd.DataFrame(columns=['Date', 'Company', 'Investment Amount', 'Industry Sector', 'US State Invested In', 'Source Country'])

# read in all csvs
for file in os.listdir('./out'):
    key = file.split('_')[0]

    print(f'Reading file {file}')

    with open(f'./out/{file}', 'r') as f:
        data = json.load(f)
    #print(data, type(data))
    try:
        obj = json.loads(data)
    except Exception as e:
        print('err:', e)
        print(data)
        continue
    df = pd.DataFrame(obj, index=[0])
    print(f'Joining document {key}')
    print(df, master_df)
    master_df = pd.merge(master_df, df, how='outer')
    #df = pd.read_json(f'./out/{file}')
    #df = pd.DataFrame(load)
    #df = pd.json_normalize(data)
    continue
    print('did not continue')
    read = []
    with open(f'./out/{file}') as f:
        print(key)
        for line in f:
            if '```' not in line:
                read.append(line)
    #df = pd.read_csv(f'./out/{file}')
    print(read)
    print(read[1:], read[0])
    exit()
    try:
        df = pd.DataFrame(read[1:], columns=read[0])

        if 'Date' in df.columns:
            print(f'Joining document {key}')
            master_df = pd.merge(master_df, df, how='outer')
        else:
            print(f'ERR: Date column not found in document {key}, format may be incorrect. Skipping for safety.')
            print(df)
    except TypeError:
        print(f'ERR: Document {key} not in CSV format. Skipping.')
print('Master DF', master_df)
