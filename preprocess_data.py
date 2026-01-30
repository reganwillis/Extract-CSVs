import re
import ollama

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

print('Extracting CSVs from documents (Ollama)..')
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
    response = ollama.generate(
        model='phi3.5:3.8b-mini-instruct-fp16',
        prompt=PROMPT,
        options={
            'temperature': 0.6,  # Adjust for creativity (0.0-1.0)
            'num_predict': 200   # Max tokens to generate
        }
    )
    print(response['response'])

    with open(f'out/{key}_out.csv', 'a') as f:
        f.write(response['response'])
