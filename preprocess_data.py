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
generator = HuggingFaceLocalGenerator(model='numind/NuExtract', huggingface_pipeline_kwargs={"model_kwargs": {"torch_dtype":torch.bfloat16, "low_cpu_mem_usage":True}})
generator.warm_up()

for key, file in data_files.items():
    print('Extracting CSV:', key)
    # generate csv output
    start = "<|input|>\nExtract information about foreign investments into Mexico City. Find what country is making the investment and for how much. Include the industrial sector by which the investment is made. If unknown write NA.### Template: {\
        \"Date\": \"\", \
        \"Company\": \"\", \
        \"Investment Amount\": \"\", \
        \"Industry Sector\": \"\", \
        \"Source Country\": \"\" \
    } \
    #### Text: "
    end = "<|output|>"
    prompt = " ".join([start, file, end])
    try:
        res = generator.run(prompt=prompt)
    except:
        print('ERR: unable to run prompt (CUDA OOM error?)')
        continue
    res = res['replies']

    with open(f'out/{key}_out.json', 'w') as f:
        json.dump(res[0].strip(), f, indent=4)
