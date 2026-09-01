import os
import re
import gzip
import requests
from warcio.archiveiterator import ArchiveIterator
from classify import load_classifier, classify
from bs4 import BeautifulSoup

# TODO: args
METHOD = "classifier"
#METHOD = "keywords"
OUT_DIR = 'dataset'

os.makedirs(OUT_DIR, exist_ok=True)

# create local dataset of all FDI articles
dataset = []

if METHOD == "classifier":
    classifier, tokenizer = load_classifier(True)
elif METHOD == "keywords":
    FDI_KEYWORDS = re.compile(r"\b(foreign direct investment|fdi|greenfield|green-field|acquire|acquisition|invests in)\b", re.I)


def strip_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style', 'noscript']):
        tag.decompose()
    text = soup.get_text(separator=' ', strip=True)
    return ' '.join(text.split())


def crawl():
    # incrementers
    crawl_count = 0
    dataset_len = 0

    # loop over all 2025 news
    INDEX = "CC-NEWS/2025"
    index_list = []
    for i in range(1, 12+1):
        i = str(i)
        if len(i) < 2:
            i = "0" + i
        index_list.append(i)

    for idx in index_list:
        full_index = INDEX + '/' + idx
        wet_url = f"https://data.commoncrawl.org/crawl-data/{full_index}/warc.paths.gz"

        with requests.get(wet_url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with gzip.GzipFile(fileobj=r.raw) as gz:
                for line in gz:
                    warc_path = line.decode('utf-8', 'ignore').strip()
                    if not warc_path:
                        continue
                    warc_url = f"https://data.commoncrawl.org/" + warc_path
                    with requests.get(warc_url, stream=True, timeout=60) as warc_resp:
                        warc_resp.raise_for_status()
                        try:
                            for rec in ArchiveIterator(warc_resp.raw):
                                if rec.rec_type != "response":
                                    continue
                                try:
                                    url = rec.rec_headers.get_header('WARC-Target-URI')
                                    text = rec.content_stream().read().decode("utf-8", "ignore")
                                    text = strip_html(text)
                                    crawl_count += 1

                                    if METHOD == "classifier":
                                        if classify(text, classifier, tokenizer):
                                            print('\nPotential FDI article found:', url)
                                            dataset.append(url+'\n'+text)
                                    elif METHOD == "keywords":
                                        if FDI_KEYWORDS.search(text):
                                            print('\nPotential FDI article found:', url)
                                            dataset.append(url+'\n'+text)

                                    # DEBUG - early stopping
                                    #if len(dataset) == 10:
                                    #    return dataset
                                    #if crawl_count == 2:
                                    #    return dataset
                                    #if idx == "02":
                                    #    print('Month 1 done..')
                                    #    return dataset
                                    
                                    # print log
                                    if crawl_count % 50 == 0:
                                        print('Articles crawled:', crawl_count)
                                        print('Potential FDI articles found:', len(dataset))
                                        print('Processing month', idx)

                                    # save dataset incrementally
                                    if dataset_len < len(dataset):
                                        with open('dataset/'+str(len(dataset))+'.txt', 'w') as f:
                                            f.write(dataset[-1])
                                        dataset_len = len(dataset)
                                except:
                                    print('ERROR: unable to process rec, skipping..')
                                    continue
                        except:
                            print('ERROR: unknown ArchiveIterator failure, skipping..')
                            continue
dataset = crawl()
print('Done.')
