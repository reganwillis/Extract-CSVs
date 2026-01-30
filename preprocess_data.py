import re
import json
import torch
from transformers import pipeline
from haystack.components.generators import HuggingFaceLocalGenerator

# split data file
print('Splitting data file by document..')
pattern = re.compile(r'^Document [a-zA-Z0-9]{25}\n$')

data_files = {}
file = ''

with open('Factiva-20260114-1825.txt', 'r', encoding='latin1') as f:
    for line in f:
        if re.match(pattern, line):
            key = line.split()[1]
            data_files[key] = file
            file = ''
            print('Processing file:', key)
        else:
            file = file + line
print("Done. Number of processed documents:", len(data_files.keys()), '\n')

print('Extracting CSVs from documents (language model)..')
generator = HuggingFaceLocalGenerator(model='numind/NuExtract', huggingface_pipeline_kwargs={"model_kwargs": {"torch_dtype":torch.bfloat16}})

#device_map="auto", low_cpu_mem_usage=True)
generator.warm_up()

for key, file in data_files.items():
    print('Extracting CSV:', key)
    # generate csv output
    PROMPT = f'Create a CSV file of content extracted from the article \
               about financial investments from countries foreign to the US \
               with columns for date, company, investment amount, \
               industry sector, US state invested in, and source country. \
               If there is not foreign investment content, or if some data \
               is unavailable, fill in the table with N\A. Provide no other text \
               besides the CSV file, starting with the first line as the \
               header for the table. {file}'

    #ollama.pull('phi3.5:3.8b-mini-instruct-fp16')
    """
    response = ollama.generate(
        model='phi3.5:3.8b-mini-instruct-fp16',
        prompt=PROMPT,
        options={
            'temperature': 0.6,  # Adjust for creativity (0.0-1.0)
            'num_predict': 200   # Max tokens to generate
        }
    )
    print(response['response'])
    """
    #generator = pipeline('text-generation', model='gpt2')
    #res = generator(PROMPT, max_length=30)
    #print(res[0]['generated_text'])
    #print(len(res))
    #for idx in res:
    #    print('\n\n', res)

    start = "<|input|>\n### Template: {\
        \"Date\": \"\", \
        \"Company\": \"\", \
        \"Investment Amount\": \"\", \
        \"Industry Sector\": \"\", \
        \"US State Invested In\": \"\", \
        \"Source Country\": \"\" \
    } \
    #### Text: "
    end = "<|output|>"
    prompt = " ".join([start, file, end])
    res = generator.run(prompt=prompt)
    res = res['replies']


    with open(f'out/{key}_out.json', 'w') as f:
        #f.write(res)
        json.dump(res[0].strip(), f, indent=4)
