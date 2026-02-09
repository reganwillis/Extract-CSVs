import os
import json
import pandas as pd

def combine_columns(df, left, right):
    # manual post-processing to correct column header errors
    try:
        df[left] = df[left].combine_first(df[right])
        df = df.drop(right, axis=1)
        print(f'INFO: column {right} merged into column {left}')
        return df
    except:
        return df

def remove_columns(df, col):
    # manual post-processing to drop extra columns
    try:
        df = df.drop(col, axis=1)
        print(f'INFO: column {col} dropped.')
        return df
    except:
        return df

master_df = pd.DataFrame(columns=['Date', 'Company', 'Investment Amount', 'Industry Sector', 'Source Country'])
master_df.columns=[c.lower() for c in master_df.columns]

# read in all csvs
for file in os.listdir('./out'):
    key = file.split('_')[0]

    print(f'Reading file {file}')

    with open(f'./out/{file}', 'r') as f:
        data = json.load(f)
    try:
        obj = json.loads(data)
        df = pd.DataFrame(obj, index=[0])
    except json.decoder.JSONDecodeError:
        print('ERR: output not in JSON format, skipping..')
        continue
    except Exception as e:
        print('ERR**:', e, type(e))
    print(f'Joining document {key}')
    try:
        df.columns=[c.lower() for c in df.columns]  # column names to lowercase
        master_df = pd.merge(master_df, df, how='outer')
    except pd.errors.MergeError:
        print('ERR: Unable to merge columns:', master_df.columns, df.columns, 'skipping..')
master_df = combine_columns(master_df, 'industry sector', 'industry')
master_df = combine_columns(master_df, 'source country', 'country')
master_df = combine_columns(master_df, 'source country', 'source')
master_df = combine_columns(master_df, 'investment amount', 'amount')
master_df = combine_columns(master_df, 'investment amount', 'investment_amount')
master_df = remove_columns(master_df, 'text')
master_df = remove_columns(master_df, 'article')
master_df = remove_columns(master_df, 'title')
master_df = remove_columns(master_df, 'byline')
master_df = remove_columns(master_df, 'language')
master_df = remove_columns(master_df, 'entity')
master_df = remove_columns(master_df, 'currency')
master_df = remove_columns(master_df, 'detail')
master_df = remove_columns(master_df, 'article title')
master_df = remove_columns(master_df, 'prediction')
master_df = remove_columns(master_df, 'author')

# write to file
with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print('Master DF', master_df)
master_df.to_csv('./out.csv')
