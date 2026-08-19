import os
import re
import csv
import json
import argparse
import pandas as pd
from transformers import pipeline
from transformers import AutoModelForCausalLM, AutoTokenizer


def init_model():
    print('Loading information extraction model (NuExtract3)')
    pipe = pipeline('text-generation', model='numind/NuExtract3', tokenizer='numind/NuExtract3')

    return pipe


def prompt_model(pipe, text):
    prompt = """
    Return ONLY valid JSON. For countries, states, and provinces, use the full name, no abbreviations.
    {
        "article_title": "Title of the article",
        "publish_date": "Date that the article was published",
        "investment_amount": "Amount of money being invested (return the full numerical value)",
        "industry_sector": "Sector that the company is in",
        "invested_country": "Country where the investment is being made",
        "recipient_state_or_province": "Subnational state/province where investment is being made (if available, if not leave blank)",
        "source_country": "Country that is making the investment in the invested country"
    }
    Text:
    {{
    """
    prompt = prompt + text + '}}'
    out = pipe(prompt, max_new_tokens=160, do_sample=False, return_full_text=False)
    out = out[0]['generated_text']

    return out


def parse_response(out):
    match = re.search(r"\{.*?}", out, re.S)
    if match:
        out = match.group(0)
    else:
        print('ERROR: Could not parse JSON.')
        return -1
    #print('Response:', out)
    data = json.loads(out)
    article_title = data.get('article_title')
    publish_date = data.get('publish_date')
    investment_amount = data.get('investment_amount')
    industry_sector = data.get('industry_sector')
    invested_country = data.get('invested_country')
    recipient = data.get('recipient_state_or_province')
    source_country = data.get('source_country')

    return [article_title, publish_date, investment_amount, industry_sector, invested_country, recipient, source_country]


if __name__ == "__main__":
    error_count = 0

    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', help='Source dataset to extract from.', type=str, default='./dataset')
    parser.add_argument('--test-dataset', help='Dataset includes ground-truth labels.', action='store_true')
    parser.add_argument('--score-only', help='Do not run pipeline, just score results.', action='store_true')
    args = parser.parse_args()

    DATASET = args.dataset

    if not args.score_only:
        pipe = init_model()

        csv_rows = []
        for file in os.listdir(DATASET):
            if file.split('.')[1] == 'txt':
                with open(DATASET + '/' + file, 'r') as f:
                    index = file.split('.')[0]
                    try:
                        text = f.read()
                        out = prompt_model(pipe, text)
                        res = parse_response(out)
                    except:
                        res = -1

                if res == -1:
                    res = [-1,-1,-1,-1,-1,-1,-1]
                    error_count += 1
                res = [str(index)] + res
                csv_rows.append(res)

        # write to CSV
        with open(f'extracted_info.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['index', 'Article Title', 'Publish Date', 'Investment Amount', 'Industry Sector', 'Invested Country', 'Recipient State/Province', 'Source Country'])
            for row in csv_rows:
                writer.writerow(row)
            print('CSV written.')

        print('Documents processed successfully:', len(csv_rows)-error_count)
        print('Documents unprocessed (error):', error_count)
        print('Done.')

    if args.test_dataset:
        #pd.set_option('display.max_rows', None)
        #pd.set_option('display.max_columns', None)
        #pd.set_option('display.width', None)
        #pd.set_option('display.max_colwidth', None)

        pred = pd.read_csv('extracted_info.csv')
        pred = pred.sort_values(by='index')
        anns = pd.read_csv(DATASET + '/labels.csv')

        #print('Comparing real vs predicted values:')
        pred = pred.set_index('index')
        anns = anns.set_index('index')
        print(pred)
        #print(anns)
        #diff = pred.set_index('index').compare(anns.set_index('index'), result_names=('Predicted', 'Actual'))
        #print('Investment Amount (Difference Report):\n', diff['Investment Amount'])
        #print('Recipient State/Province (Difference Report):\n', diff['Recipient State/Province'])
        #print('Source Country (Difference Report):\n', diff['Source Country'])

        col = 'Investment Amount'
        ia_acc = (pred[col] == anns[col]).mean()
        col = 'Invested Country'
        ic_acc = (pred[col] == anns[col]).mean()
        col = 'Recipient State/Province'
        rep_acc = (pred[col] == anns[col]).mean()
        col = 'Source Country'
        sc_acc = (pred[col] == anns[col]).mean()

        print('\n***TEST DATASET ACCURACY SCORE***')
        print('Accuracy of Investment Amount:', ia_acc)
        print('Accuracy of Invested Country:', ic_acc)
        print('Accuracy of Recipient State/Province:', rep_acc)
        print('Accuracy of Source Country:', sc_acc)
