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
    try:
        obj = json.loads(data)
        df = pd.DataFrame(obj, index=[0])
    except Exception as e:
        print('ERR:', e)
        continue
    print(f'Joining document {key}')
    master_df = pd.merge(master_df, df, how='outer')
with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print('Master DF', master_df)

#master_df['Investment Amount'] = master_df['Investment Amount'] + master_df['Amount']
#master_df.apply(lambda row: if 'Investment Amountaxis=1)
master_df['Investment Amount'] = master_df['Investment Amount'].combine_first(master_df['Amount'])
master_df = master_df.drop('Amount', axis=1)
master_df['Source Country'] = master_df['Source Country'].combine_first(master_df['Country of Origin'])
master_df = master_df.drop('Country of Origin', axis=1)
master_df['Source Country'] = master_df['Source Country'].combine_first(master_df['Country'])
master_df = master_df.drop('Country', axis=1)
master_df.to_csv('./out.csv')
