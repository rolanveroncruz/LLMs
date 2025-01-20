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


start_time = datetime.now()
print(f"Now is: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

load_dotenv()
##############
# Step One: Gather all docs, run them through UnstructuredHTMLLoader
##############
file_path = "../scrapeLaws/data/decisions/2024/Apr/A.C. No. 10627 (from A.C. No. 6622).html"
data_path = "../scrapeLaws/data"
docs = []
total_docs = 0
for root, dirs, files in os.walk(data_path):
    for file in files:
        filename, file_extension = os.path.splitext(file)
        if file_extension == ".html":
            file_path = os.path.join(root, file)
            total_docs += 1
            loader_uns = UnstructuredHTMLLoader(file_path)
            print(f"processing: {file_path}")
            try:
                for doc in loader_uns.load():
                    docs.append(doc)
            except UnicodeDecodeError:
                print(f"*******Problem with****: {file_path} *********************************************************************")
print(f"Total documents: {total_docs}")
print(f"Total Documents: {len(docs)}")
print(f"Step One Done.")


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # chunk size (characters)
    chunk_overlap=200,  # chunk overlap (characters)
    add_start_index=True,  # track index in original document
)
all_splits = text_splitter.split_documents(docs)
string_rep = dumps(all_splits)
with open("./data/all_splits.json", "w") as outfile:
    json.dump(string_rep, outfile)

exit(0)


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
