import os
import re
import csv
import json
import html
import torch
from transformers import pipeline
import xml.etree.ElementTree as ET

root = './data/'
datasets = ['']

print('Loading information extraction model (NuExtract3)')
pipe = pipeline('text-generation', model='./NuExtract3', tokenizer='./NuExtract3')

for dataset in datasets:
    dataset_path = root + dataset + '/'
    out_dir = dataset + '_out'
    os.makedirs(out_dir, exist_ok=True)
    print('Dataset:', dataset)

    print('Extracting FDI information from documents..')
    for file in os.listdir(dataset_path):
        if file.split('.')[0] + '_out.csv' in os.listdir(out_dir):
            print(file, '-- file already processed, skipping..')
            continue
        print('Extracting data from file:', file)

        # read/parse file
        tree = ET.parse(dataset_path+file)
        root = tree.getroot()
        try:
            title = root.findtext('.//TitleAtt/Title', default='NA')
            date = root.findtext('.//NumericDate', default='NA')
            text_elem = root.find('.//TextInfo/Text')
            text = text_elem.text
            text = html.unescape(text)
            text = re.sub(r"<[^>]", " ", text)
            text = re.sub(r"\s+", " ", text)
        except AttributeError as e:
            print('ERROR:', e, 'continuing..')
            continue

        # extract information from LLM
        prompt = """
        Return ONLY valid JSON.
        {
            "fdi_event": "If the article refers to an FDI event (true or false),
            "company": "Name of the company investing",
            "investment_amount": "Amount of money being invested",
            "industry_sector": "Sector that the company is in",
            "foreign_country": "The country that is the source of investment"
        }
        Text:
        {{
        """
        prompt = prompt + text + '}}'
        out = pipe(prompt, max_new_tokens=80, do_sample=False, return_full_text=False)
        out - out[0]['generated_text']

        # parse model response
        print(title, date)
        match = re.search(r"\{.*?}", out, re.S)
        if match:
            out = match.group(0)
        else:
            print('ERROR: No JSON provided in response.')
            exit()  # DEBUG
            continue
        print('Response:', out)
        data = json.loads(out)
        fdi_event = data.get('fdi_event')
        company = data.get('company')
        investment_amount = data.get('investment_amount')
        industry_sector = data.get('industry_sector')
        source_country = data.get('source_country')

        # write to CSV
        key = file.split('.')[0]
        with open(f'{out_dir}/{key}_out.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow([title, data, fdi_event, company, investment_amound, industry_sector, source_country])
            print('CSV written.')
    print(f'Dataset {dataset} completed.')
print('Done.')
