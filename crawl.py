import re
import gzip
import requests
from warcio.archiveiterator import ArchiveIterator

# TODO: create local dataset of all FDI articles
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
                #print(text[:1500])
                dataset.append(uri)
                break

print(dataset)

exit()

import re
import requests
import trafilatura
from bs4 import BeautifulSoup

# TODO: create local dataset of all FDI articles

FDI_KEYWORDS = re.compile(r"\b(foreign direct investment|fdi|greenfield|green-field|acquire|acquisition|invests in)\b", re.I)

#url = "https://www.reuters.com/business/"
url = "https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-21/"
print('Attempting to crawl', url, '..')
headers = {"User-Agent": "Mozilla/5.0"}
resp = requests.get(url, headers=headers, timeout=20)
print(resp.status_code)

links = {
    a['href'] if a['href'].startswith('http') else 'https://www.reuters.com' + a['href']
    for a in BeautifulSoup(resp.text, 'html.parser').find_all('a', href=True)
    if 'reuters.com' in a['href']
}

for url in sorted(links):
    resp = requests.get(url, headers=headers, timeout=20)
    text = trafilatura.extract(resp.text, include_comments=False, include_tables=False)

    # TODO: use FDI classifier instead of regex search
    if FDI_KEYWORDS.search(text):
        print('FDI article found:', url)
        print(text[:1500])

exit()




import requests
import json

# For parsing URLs:
from urllib.parse import quote_plus

# For parsing WARC records:
from warcio.archiveiterator import ArchiveIterator

# The URL of the Common Crawl Index server
SERVER = 'http://index.commoncrawl.org/'

# The Common Crawl index you want to query
INDEX_NAME = 'CC-MAIN-2024-33'      # Replace with the latest index name

# The URL you want to look up in the Common Crawl index
target_url = 'commoncrawl.org/faq'  # Replace with your target URL

# It’s advisable to use a descriptive User-Agent string when developing your own applications.
# This practice aligns with the conventions outlined in RFC 7231. Let's use this simple one:
myagent = 'cc-get-started/1.0 (Example data retrieval script; yourname@example.com)'

# Function to search the Common Crawl Index
def search_cc_index(url):
    encoded_url = quote_plus(url)
    index_url = f'{SERVER}{INDEX_NAME}-index?url={encoded_url}&output=json'
    response = requests.get(index_url, headers={'user-agent': myagent})
    print("Response from server:\r\n", response.text)
    if response.status_code == 200:
        records = response.text.strip().split('\n')
        return [json.loads(record) for record in records]
    else:
        return None

# Function to fetch content from Common Crawl
def fetch_page_from_cc(records):
    for record in records:
        offset, length = int(record['offset']), int(record['length'])
        s3_url = f'https://data.commoncrawl.org/{record["filename"]}'

        # Define the byte range for the request
        byte_range = f'bytes={offset}-{offset+length-1}'

        # Send the HTTP GET request to the S3 URL with the specified byte range
        response = requests.get(
            s3_url,
            headers={'user-agent': myagent, 'Range': byte_range},
            stream=True
        )

        if response.status_code == 206:
            # Use `stream=True` in the call to `requests.get()` to get a raw
            # byte stream, because it's gzip compressed data

            # Create an `ArchiveIterator` object directly from `response.raw`
            # which handles the gzipped WARC content

            stream = ArchiveIterator(response.raw)
            for warc_record in stream:
                if warc_record.rec_type == 'response':
                    return warc_record.content_stream().read()
        else:
            print(f"Failed to fetch data: {response.status_code}")
            return None

    print("No valid WARC record found in the given records")
    return None

# Search the index for the target URL
records = search_cc_index(target_url)
if records:
    print(f"Found {len(records)} records for {target_url}")

    # Fetch the page content from the first record
    content = fetch_page_from_cc(records)
    if content:
        print(f"Successfully fetched content for {target_url}")
        # You can now process the 'content' variable as needed
        # using something like Beautiful Soup, etc
else:
    print(f"No records found for {target_url}")

