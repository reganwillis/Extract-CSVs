import os
import pandas as pd

master_df = pd.DataFrame()

# read in all csvs
for file in os.listdir('./out'):
    key = file.split('_')[0]

    print(f'Reading file {file}')
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
