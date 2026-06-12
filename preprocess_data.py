import re
import json
import torch
from transformers import pipeline
from haystack.components.generators import HuggingFaceLocalGenerator

print('Loading model')
generator = HuggingFaceLocalGenerator(model='numind/NuExtract', huggingface_pipeline_kwargs={"model_kwargs": {"torch_dtype":torch.bfloat16, "low_cpu_mem_usage":True}})
generator.warm_up()

print('Extracting CSVs from documents (language model)..')
for key, file in data_files.items():
    print('Extracting CSV:', key)
    # generate csv output
    start = "<|input|>\nExtract information about foreign investments into Mexico City from news articles. Write the date the article was published, the company that made the investment, and the country that made the investment and for how much. Include the industrial sector by which the investment is made. If unknown write NA.### Template: {\
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
