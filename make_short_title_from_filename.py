"""
This script is to create a dict of "long_title" -> "short_title" for all the legal documents.
In addition, it creates a file of a summary of the legal document with the short title as the filename.

"""
import os
import  bs4
from gem_funcs import make_short_title, make_brief
from langchain_community.document_loaders import UnstructuredHTMLLoader
import json
from pathlib import Path

"""
Prepare the "long_title"-> "short_title" map. set it to an empty dict first.
But if the file already exists, then set it to that file's contents.
"""
long_to_short_title_map = {}
the_current_dir = os.path.dirname(os.path.realpath(__file__))
long_to_short_title_map_json_file = os.path.join(the_current_dir, "data", "long_to_short_title_map.json")
if os.path.exists(long_to_short_title_map_json_file):
    map_file_h = open(long_to_short_title_map_json_file, 'r')
    long_to_short_title_map = json.load(map_file_h)



def get_doctype(root: str) ->str:
    """
    Return the doctype, e.g. "decision", "executive_issuance", etc from the path.
    :param root:
    :param path:
    :return:
    """
    path_arr = root.split("/")
    return path_arr[3]

def make_subtitle_from_path(root: str) -> str:
    path_arr = root.split("/")
    if len(path_arr)>=7:
        return path_arr[6] + " " + path_arr[5]
    else:
        return None

def process_file(root, file, doc_count):
    summarized_path = os.path.join(the_current_dir, "data", "summaries")

    full_path = os.path.join(root, file)
    the_file = open(full_path, "r")
    soup = bs4.BeautifulSoup(the_file, "lxml")
    title = soup.h3.text
    if title is None or title == "":
        title = file.split(".")[0]
    h2_tags = soup.findAll("h2")
    sub_title = " "
    for h2_tag in h2_tags:
        sub_title = sub_title + h2_tag.text
    if sub_title is None or sub_title == "" or sub_title == " ":
        sub_title = make_subtitle_from_path(root)
    if len(title) < 100 and (sub_title == ' ' or sub_title == "" or sub_title is None):
        short_title = title
    else:
        possible_short_title = make_short_title(title, sub_title)

        if possible_short_title is not None:
            short_title = possible_short_title.text
            print(f"short title is: {possible_short_title.text}")
        else:
            short_title = title
    if short_title is None:
        print("WE have a short_title is None problem.")

    # if short_title has "/", replace them with "_" to avoid folder issues.
    if '/' in short_title:
        short_title = short_title.replace("/", "_")

    # now have the short_title, store to map and save map to file.
    long_to_short_title_map[file] = short_title
    outfile = open(long_to_short_title_map_json_file, 'w')
    json.dump(long_to_short_title_map, outfile)
    outfile.flush()
    os.fsync(outfile.fileno())

    # Work on the summary
    docs = UnstructuredHTMLLoader(full_path).load()
    summary = make_brief(docs[0].page_content)
    doctype = get_doctype(full_path)
    summary_destination = os.path.join(summarized_path, doctype)
    Path(summary_destination).mkdir(parents=True, exist_ok=True)
    summary_file = os.path.join(summary_destination, short_title + ".md")
    print(f"writing summary to: {summary_file}")
    f= open(summary_file, 'w', 1)
    f.write(summary)
    f.flush()
    os.fsync(f.fileno())
    print("done.")


def main():
    data_path = "../scrapeLaws/data"
    the_current_dir = os.path.dirname(os.path.realpath(__file__))
    problem_docs = []
    doc_count = 0
    for root, dirs, files in os.walk(data_path):
        for file in files:
            full_path = os.path.join(root, file)
            ### check if file is in the map. if yes, skip.
            map_keys = long_to_short_title_map.keys()
            if file in map_keys:
                print(f"****** skipping {full_path}...")
                continue

            try:
                print(f"working on {full_path}...")
                process_file(root, file, doc_count)
            except Exception as e:
                print(f"problem with {full_path}...")
                problem_docs.append(full_path)
                problem_docs_path = os.path.join(the_current_dir, "data", "problem_docs.json")
                problems =  open(problem_docs_path, "w")
                json.dump(problem_docs, problems)
                problems.flush()
                os.fsync(problems.fileno())
                continue





if __name__ == "__main__":
    main()
