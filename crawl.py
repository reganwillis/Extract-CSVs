import re
import gzip
import requests
from warcio.archiveiterator import ArchiveIterator

# create local dataset of all FDI articles
dataset = []

FDI_KEYWORDS = re.compile(r"\b(foreign direct investment|fdi|greenfield|green-field|acquire|acquisition|invests in)\b", re.I)

# TODO: loop over all indexes from the past five years
INDEX = "CC-MAIN-2025-38"
WET_LIST = f"https://data.commoncrawl.org/crawl-data/{INDEX}/wet.paths.gz"

def iter_wet_urls():
    with requests.get(WET_LIST, stream=True, timeout=30) as r:
        r.raise_for_status()
        for line in gzip.GzipFile(fileobj=r.raw):
            yield "https://data.commoncrawl.org/" + line.decode("utf-8").strip()

for wet_url in iter_wet_urls():
    with requests.get(wet_url, stream=True, timeout=60) as r:
        r.raise_for_status()
        for rec in ArchiveIterator(r.raw):
            if rec.rec_type != "conversion":
                continue
            uri = rec.rec_headers.get_header("WARC-Target-URI")
            text = rec.content_stream().read().decode("utf-8", "ignore")
            # TODO: use FDI classifier instead of regex search
            if FDI_KEYWORDS.search(text):
                print('\nPotential FDI article found:', uri)
                dataset.append(uri)
                break

print(dataset)
