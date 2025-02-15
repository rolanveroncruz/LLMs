"""
This script splits the html files in the ../scrapeLaws/data folder into LangChain docs, and writes them into
data/all_splits.json
"""
from langchain_community.document_loaders import  UnstructuredHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv
from datetime import datetime
from langchain_core.load import dumps
from langchain_core.documents import Document
import json
import random


def get_url(path:str, file_name:str) ->str|None:
    """
    From the path of the file and its filename, we look for the appropriate json file, and get the doc_number doc_type_number.
    From these, we can form the url as: f"https://elibrary.judiciary.gov.ph/thebookshelf/showdocs/{document_number[0]}/{document_number[1]}"
    *** A Problem though is that when the files were scraped into the local folder, the filenames had to be truncated when
    path+"/"+file_name were longer than 100 characters. However in the json files, the keys (filenames) were not trucated.
    Therefore, the filenames we're iterative over is shorter than the actual filename-key.
    The solution is if we don't have a key match, we get the closest matching key.

    :param path:
    :param file_name:
    :return:
    """
    json_file_base_path = "../scrapeLaws/00_"
    doc_name, file_ext= os.path.splitext(file_name)


    if file_ext == ".html":
        path_arr = path.split('/')
        # path_arr = ['..', 'scrapeLaws', 'data', 'decisions', '2024', 'Apr', '']
        if path_arr[-1] == '':
            type_index = -4
        else:
            type_index = -3
        subtype_index = type_index - 1
        if path_arr[type_index] == 'decisions':
            doc_type_name = 'decisions'
        else:
            doc_type_name = path_arr[subtype_index] + '_' + path_arr[type_index]
        json_file_name = json_file_base_path + doc_type_name + '.json'
        print(f"json_file_name: {json_file_name}")
        print(f"key is:{doc_name}")
        json_file = json.load(open(json_file_name, "r"))
        document_number = json_file.get(doc_name, None)
        if document_number is not None:
            return f"https://elibrary.judiciary.gov.ph/thebookshelf/showdocs/{document_number[0]}/{document_number[1]}"
        else:
            # we don't have a filename-key match, find the best one, defined as the string whose substring is the doc_name.
            filename_keys = json_file.keys()
            matches = [s for s in filename_keys if doc_name in s]
            if len(matches) ==0:
                print(f"Problem with {doc_name} in {json_file_name}")
                return None
            if len(matches) == 1:
                document_number = json_file[matches[0]]
                return f"https://elibrary.judiciary.gov.ph/thebookshelf/showdocs/{document_number[0]}/{document_number[1]}"
            elif len(matches)==2:
                # flip a coin.
                toss_head = random.randrange(0,2)
                if toss_head:
                    document_number = json_file[matches[0]]
                else:
                    document_number = json_file[matches[1]]
            elif len(matches)>2:
                print(f"Problem with {doc_name} in {json_file_name}")




def update_metadata(doc_to_update: Document, doc_to_update_number: int,name:str, title:str) -> None:
    """
    Given a Document and its doc_number, update the metadata. Specifically, we need to provide
    the name, title, and url.
    :param doc_to_update:
    :param doc_to_update_number:
    :param name:
    :param title:
    :return:
    """

def get_doc_title(path:str, file_name:str)->str:
    """

    :param path:
    :param file_name:
    :return:
    """

def main():
    start_time = datetime.now()
    print(f"Now is: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    load_dotenv()
    ##############
    # Step One: Gather all docs, run them through UnstructuredHTMLLoader
    ##############
    data_path = "../scrapeLaws/data"
    docs = []
    total_docs = 0
    for root, dirs, files in os.walk(data_path):
        # in the first pass,
        # root = ../scrapeLaws/data; # dirs = ['treaties', 'decisions', 'executive_issuance', 'laws', 'references'];
        # files = []
        # in the second pass
        # root = "../scrapeLaws/data/treaties; # dirs = ['regional','bilateral']; # files = []
        # and so on, we expect that eventually, all files will be seen.

        for file in files:
            # here, file will have just the filename, and root will be the path to the file.
            # from the root and filename, we should get the doc_number
            doc_url= get_url(root, file)
            filename, file_extension = os.path.splitext(file)
            if file_extension == ".html":
                doc_title = get_doc_title(root, file)
                file_path = os.path.join(root, file)
                total_docs += 1
                loader_uns = UnstructuredHTMLLoader(file_path)
                print(f"processing: {file_path}")
                try:
                    for doc in loader_uns.load():
                        # here, doc is a Document
                        update_metadata(doc_to_update=doc, doc_to_update_number=doc_number, name=filename, title=doc_title)
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


if __name__ == "__main__":
    main()