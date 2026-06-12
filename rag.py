import os
import pandas as pd
from llama_index.core import Settings
from llama_index.core import PromptTemplate
from llama_index.readers.file import XMLReader
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

print('Importing dataset..')
dataset_path = './data/'

# TODO: any necessary parsing

print('Done.')

print('Embedding dataset..')
embed_model = HuggingFaceEmbedding(model_name='./BAAI/bge-small-en-v1.5')
Settings.embed_model = embed_model
Settings.chunk_size = 512
index = VectorStoreIndex.from_documents(documents)
print('Done.')

print('Initializing model..')
sys_prompt = "You are an information extraction model. Your goal is to answer questions accurately using only the context provided. The questions are aimed towards understanding foreign investment."
query_wrapper_prompt = PromptTemplate("<|USER|>{query_str}<|ASSISTANT|>")
model = HuggingFaceLLM(system_prompt=sys_prompt, query_wrapper_prompt=query_wrapper_prompt, tokenizer_name='./NuExtract3', model_name='./NuExtract3', device_map='auto')
Settings.llm = model
query_engine = index.as_query_engine()
print('Done.')

print('Querying model..')
response = query_engine.query('How much money has the US invested in Mexico?', similarity_top_k=20)
print(response)
print('Done. Exiting..')
