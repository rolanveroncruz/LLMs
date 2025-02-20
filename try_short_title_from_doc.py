import os
import bs4
import ollama
from langchain_community.document_loaders import UnstructuredHTMLLoader
import time
from dotenv import load_dotenv
from google import genai
load_dotenv()


def get_short_title_gemini(title, subtitle):
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    user_message = (f"Give a shorter title for the title of the following legal document:'{title} {subtitle}'. "
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
        possible_short_title = bs4.BeautifulSoup(response.text, "lxml").title
        if possible_short_title is not None:
            not_ok = False #break out of loop
        else:
            not_ok = True # keep looping
            time.sleep(2)
    return possible_short_title


def get_short_title_from(title, subtitle):
    user_message = (f"Give a shorter title for the title of the following legal document:'{title} {subtitle}'. "
                    "If the title is short enough, you may keep it as is."
                    f"Include document serial numbers, petitioners and respondents when applicable, "
                    f"as well as the month and year of the document in the title. Surround your answer "
                    f"with the following tags <title> </title>")
    messages = [{"role": "system",
                "content": "You are a legal assistant. Give the most concise answers without loss of meaning."},
               {"role": "user",
                "content":user_message }]
    not_ok = True
    count_attempts = 0
    possible_short_title = None
    while not_ok and count_attempts < 3:
        count_attempts +=1
        chat_response = ollama.chat(model="llama3.2", messages=messages)['message']['content']
        possible_short_title = bs4.BeautifulSoup(chat_response, "lxml").title
        if possible_short_title is not None:
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


def summarize(doc: str):
    user_message = (f"Summarize this legal document for a lawyer, "
                    f"highlighting key provisions, obligations, liabilities, and potential risks. "
                    f"Focus on relevant case law, statutory references, and any ambiguous or contentious clauses. "
                    f"Keep it concise but legally precise. Please format the output in markdown format."
                    f"Contents: \n{doc}")
    messages = [{"role": "system",
                 "content": "Provide the output in markdown format."},
                {"role": "user",
                 "content":user_message }]
    response = ollama.chat(model="llama3.2", messages=messages)['message']['content']
    return response



#sample_file = "/home/rolanvc/LLMs/scrapeLaws/data/decisions/1996/Apr/A.M. No. P-95-1133.html"
sample_file ="/home/rolanvc/LLMs/scrapeLaws/data/decisions/2021/May/G.R. No. 196359.html"

def main():
    the_file = open(sample_file, "r")
    soup = bs4.BeautifulSoup(the_file, "lxml")
    title = soup.h3.text
    h2_tags = soup.findAll("h2")
    sub_title = " "
    for h2_tag in h2_tags:
        sub_title = sub_title + h2_tag.text
    short_title = get_short_title_from(title, sub_title)
    print(f"short_title: {short_title}")
    docs = UnstructuredHTMLLoader(sample_file).load()
    summary = summarize(docs[0].page_content)
    print(f"summary: {summary}")


if __name__ == "__main__":
    main()