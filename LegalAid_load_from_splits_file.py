import json

from langchain_core.load import loads
# from langchain_voyageai import VoyageAIEmbeddings
from langchain_ollama import OllamaEmbeddings
import os
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
import time
from datetime import datetime


load_dotenv()
VOYAGE_API_KEY = os.environ["VOYAGE_LEGALAID_API_KEY"]
QDRANT_URL = os.environ["QDRANT_LOCATION"]
QDRANT_API_KEY = os.environ["QDRANT_KEY"]
QDRANT_LOCAL_DOCKER = os.environ["QDRANT_LOCAL_DOCKER"]


start_time = datetime.now()
print(f"Now is: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

with open("./data/all_splits.json", "r") as infile:
    all_splits = loads(json.load(infile))

embeddings = OllamaEmbeddings(model="llama3.2")

num_parts = 100
part = len(all_splits)//num_parts
print(f"Total Splits: {len(all_splits)}")
print(f"number of parts: {num_parts}")
print(f"size of each part:{part}")


for i in range(num_parts):
    print(f"iteration#: {i}")
    delay = 60
    print(f"sleeping for {delay//60} minutes.")
    time.sleep(delay)
    start_idx = i*part
    end_idx = min((i+1)*part-1, len(all_splits))
    print(f"uploading records: {start_idx} to {end_idx} ")
    qd_start = time.time()
    qdrant_a = QdrantVectorStore.from_documents(documents=all_splits[start_idx:end_idx], embedding=embeddings,
                                                url=QDRANT_LOCAL_DOCKER, collection_name="legal_docs_voyageai")
    qd_end = time.time()
    print(f"upload took {(qd_end - qd_start)/60} minutes")
    now_datetime = datetime.now()
    time_from_start = (now_datetime - start_time).total_seconds()

    print(f"minutes from start:{time_from_start} minutes")

print("Done")
