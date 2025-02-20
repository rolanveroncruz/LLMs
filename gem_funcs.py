import os
import bs4
import ollama
from langchain_community.document_loaders import UnstructuredHTMLLoader
import time
from dotenv import load_dotenv
from google import genai
load_dotenv()


def make_short_title(title, subtitle):
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    user_message = (f"Give only one shorter title for the title of the following legal document:'{title} {subtitle}'. "
                    "If the title is short enough, you may keep it as is."
                    f"Include document serial numbers, petitioners and respondents when applicable, "
                    f"as well as the month and year of the document in the title. Surround your answer "
                    f"with the following tags <title> </title>")
    client = genai.Client(api_key=GEMINI_API_KEY)
    not_ok = True
    count_attempts = 0
    possible_short_title = None
    while not_ok and count_attempts < 3:
        count_attempts +=1
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[f"{user_message}"])
        """ check for validity
        1. it should be surrounded by title tags.
        2. it should only be one line long.
        """
        possible_short_title = bs4.BeautifulSoup(response.text, "lxml").title
        if ((possible_short_title is not None)
                and ("/n" not in possible_short_title)
                and ("/r" not in possible_short_title)) :
            possible_short_title = possible_short_title
            not_ok = False #break out of loop
        else:
            not_ok = True # keep looping
            time.sleep(2)
    return possible_short_title


def make_brief(doc:str):
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    user_message = (f"Summarize this legal document for a lawyer, "
                    f"highlighting key provisions, obligations, liabilities, and potential risks. "
                    f"Focus on relevant case law, statutory references, and any ambiguous or contentious clauses. "
                    f"Keep it concise but legally precise. Please format the output in markdown format."
                    f"Contents: \n{doc}")
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[f"{user_message}"])
    return response.text


