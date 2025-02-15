"""
 This script takes the langchain Documents in data/all_splits.json, and uploads them to Qdrant using VoyageAI embeddings.
"""
from langchain_community.document_loaders import BSHTMLLoader, UnstructuredHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_voyageai import VoyageAIEmbeddings
import os
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
import time
from datetime import datetime
from langchain_core.load import dumps
import json

all_splits = json.load(open("data/all_splits.json"))
start_time = datetime.now()

VOYAGE_API_KEY=os.environ["VOYAGE_LEGALAID_API_KEY"]
emb_vectors = []
embeddings = VoyageAIEmbeddings(model="voyage-law-2", api_key=VOYAGE_API_KEY)
QDRANT_URL=os.environ["QDRANT_LOCATION"]
QDRANT_API_KEY=os.environ["QDRANT_KEY"]
QDRANT_LOCAL_DOCKER=os.environ["QDRANT_LOCAL_DOCKER"]

num_parts = 100
part = len(all_splits)//num_parts
print(f"Total Splits: {len(all_splits)}")
print(f"number of parts: {num_parts}")
print(f"size of each part:{part}")


for i in range(num_parts):
    print(f"iteration#: {i}")

    print("sleeping for one minute.")
    time.sleep(120)
    start_idx = i*part
    end_idx = min((i+1)*part-1, len(all_splits))
    print(f"uploading records: {start_idx} to {end_idx} ")
    qd_start = time.time()
    qdrant_a = QdrantVectorStore.from_documents(documents=all_splits[start_idx:end_idx], embedding=embeddings,
                                                url=QDRANT_LOCAL_DOCKER, collection_name="legal_docs")
    qd_end = time.time()
    print(f"upload took {(qd_end - qd_start)/60} minutes")


end_time = datetime.now()
print(f"Now is: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Total time to run: {(end_time - start_time).total_seconds()/60} minutes")
print("end.")
# Without uploading to Qdrant, total run time is about 88 mins or 1hr28 mins.
# Total Documents is 89748 (90k)
# Total Splits is 1,793,918 (1794k)
