# Feb 18, 20025 afternoon
Pycharm became unresponsive earlier. I couldn't get anywork done on any pycharm 
instance so i rebooted my desktop. So now, i'm modifying `make_short_title_from_filename`
so that anytime i have to stop it, i can easily resume it later.


# Feb 18, 20025 morning 
I am already successfully running `make_short_title_from_filename.py`. This
should go through all the legal documents and computing a short_title and summary for each one.
Then a map is created in `datqa/long_to_short_title_map.json` which maps the
`long_file_name` -> `short_title`. The summary is stored in an `.md` file with filename `doctype/short_title.md`

Once the `make_short_title_from_filename.py` has finished. I will return to the main task of updating the Qdrant db.
This task first requires:
1. updating the metadata in each Document. The metadata are:
  - long title
  - short_title
  - url
  - doc_number
2. splitting the Documents and saving all the splits.
3. uploading the splits.