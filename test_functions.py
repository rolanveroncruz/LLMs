from LegalAid_doc_splitter import get_url, get_doc_title
import os


sample_path = "../scrapeLaws/data/decisions/2024/Apr/"
sample_file = "A.M. No. SC-23-001 [Formerly JIB FPI No. 22-008-SC].html"

doc_numer = get_url(path=sample_path, file_name=sample_file)
print(f"url: {doc_numer}")
doc_title = get_doc_title(path=sample_path, file_name=sample_file)
print(f"doc_title: {doc_title}")


def main():
    data_path = "../scrapeLaws/data"
    docs = []
    total_docs = 0
    for root, dirs, files in os.walk(data_path):
        for file in files:
            # here, file will have just the filename, and root will be the path to the file.
            # from the root and filename, we should get the doc_number
            filename, file_extension = os.path.splitext(file)
            if file_extension == ".html":
                doc_url = get_url(path=root, file_name=file)
                if doc_url is not None:
                    print(f"url: {doc_url}")
                else:
                    print(f"Problem: {root}/{file}")


if __name__ == "__main__":
    main()