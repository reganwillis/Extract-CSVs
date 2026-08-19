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
    Return ONLY valid JSON.
    {
        "fdi_event": "If the article refers to an FDI event (true or false)",
        "article_title": "Title of the article",
        "publish_date": "Date that the article was published",
        "company": "Name of the company investing",
        "investment_amount": "Amount of money being invested",
        "industry_sector": "Sector that the company is in",
        "invested_country": "Country where the investment is being made",
        "recipient_state_or_province": "Subnational state/province where investment is being made (if available, if not leave blank)",
        "source_country": "Country that is making the investment in the invested country"
        ""
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
    fdi_event = data.get('fdi_event')
    article_title = data.get('article_title')
    publish_date = data.get('publish_date')
    company = data.get('company')
    investment_amount = data.get('investment_amount')
    industry_sector = data.get('industry_sector')
    invested_country = data.get('invested_country')
    recipient = data.get('recipient_state_or_province')
    source_country = data.get('source_country')

    return [article_title, publish_date, fdi_event, company, investment_amount, industry_sector, invested_country, recipient, source_country]


if __name__ == "__main__":
    error_count = 0

    # TODO: args
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', help='Source dataset to extract from.', type=str, default='./dataset')
    parser.add_argument('--test-dataset', help='Dataset includes ground-truth labels.', action='store_true')
    args = parser.parse_args()

    DATASET = args.dataset

    pipe = init_model()

    csv_rows = []
    for file in os.listdir(DATASET):
        with open(DATASET + '/' + file, 'r') as f:
            index = file.split('.')[0]
            try:
                text = f.read()
                out = prompt_model(pipe, text)
                res = parse_response(out)
            except:
                res = -1

        if res == -1:
            res = [index,-1,-1,-1,-1,-1,-1,-1,-1]
            error_count += 1
        res = [str(index)] + res
        csv_rows.append(res)

    # write to CSV
    with open(f'extracted_info.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['index', 'Article Title', 'Publish Date', 'FDI Event', 'Investment Amount', 'Industry Sector', 'Invested Country', 'Recipient State/Province', 'Source Country'])
        for row in csv_rows:
            writer.writerow(row)
        print('CSV written.')

    print('Documents processed successfully:', len(csv_rows))
    print('Documents unprocessed (error):', error_count)
    print('Done.')

    # TODO: automate
    if args.test_dataset:
        print('Scoring real vs predicted values:')
        pred = pd.read_csv('extracted_info.csv')
        anns = pd.read_csv(DATASET + '/labels.csv')

        print(pred)
        print(anns)
