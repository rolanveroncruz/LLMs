#!/usr/bin/env python
# coding: utf-8
from langchain_voyageai import VoyageAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_ollama.llms import OllamaLLM
import os
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from dotenv import load_dotenv
from langchain_core.documents import Document
from deepseek import DeepSeekAPI
from langchain_openai import ChatOpenAI

load_dotenv()
####################
#
# Setup the env vars
#
####################

QDRANT_CLOUD_URL = os.environ["QDRANT_CLOUD_URL"]
QDRANT_CLOUD_API_KEY = os.environ["QDRANT_CLOUD_API_KEY"]
LANGSMITH_TRACING = True
LANGSMITH_ENDPOINT = "https://api.smith.langchain.com"
LANGSMITH_API_KEY = "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"
LANGSMITH_PROJECT = "pr-linear-offense-26"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VOYAGE_LEGALAID_API_KEY = os.getenv("VOYAGE_LEGALAID_API_KEY")
os.environ["OLLAMA_HOST"] = "192.168.68.107"
os.environ["OLLAMA_PORT"] = "8080"
####################
#
# Setup the components
#
####################

embeddings = VoyageAIEmbeddings(model="voyage-law-2", api_key=VOYAGE_LEGALAID_API_KEY)
# embeddings = OllamaEmbeddings(model="llama3.2")
client = QdrantClient(url=QDRANT_CLOUD_URL, api_key=QDRANT_CLOUD_API_KEY)
vector_store = QdrantVectorStore(client=client, embedding=embeddings, collection_name="legal_docs_voyage")
llm = ChatOpenAI(model="o1-mini", api_key=OPENAI_API_KEY)
# test_prompt = "What are the things to be considered in invoking and proving psychological incapacity?"
# test_docs = vector_store.similarity_search(test_prompt)


# prompt = hub.pull("rlm/rag-prompt", api_key=LANGSMITH_API_KEY)
# prompt is a ChatPromptTemplate
system_prompt = ("You are a legal assistant of a lawyer."
                 "Use only the following pieces of retrieved context to answer the question."
                 "Be as detailed as possible. And cite sources if possible."
                 "If you don't know the answer, just say that you don't know. ")

prompt = ChatPromptTemplate([
                             ("human", system_prompt + "\nquestion:{question}\n context:{context}\n"),
                             ])
example_messages = prompt.invoke({
    "context": "(context goes here)",
    "question": "(question goes here)"}
).to_messages()
assert len(example_messages) == 1
print(example_messages[0].content)


####################
#
#  Build the graph.
#
####################
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


def retrieve(state: State):
    """

    :param state: a dict of {"question": 'What....?"}
    :return: dict {"context": [Document]}. [Document] is a list of langchain Documents
    A langchain Doc has fields: metadata and page_content
    """

    retrieved_docs = vector_store.similarity_search(state["question"], k=10)
    print(f"retrieved {len(retrieved_docs)} documents")
    print("****")
    return {"context": retrieved_docs}


def generate(state: State):
    # state now is dict of {"question": "...", "context": [doc]}
    docs_content = "\n\n".join(f"{doc.page_content} Source:{get_source(doc)}" for doc in state["context"])
    # TODO: make the source a <a href /> so user can open it to supreme court e-library.
    # docs_content is now a long string of the various contents of the context list.
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    # messages is now a ChatPromptValue.
    response0 = llm.invoke(messages)
    return {"answer": response0.content}


def get_source(doc: Document) -> str:
    """
    Given doc, a Langchain Document, compute the source, the title and date of the document.

    :param doc:
    :return:
    """
    src = doc.metadata["source"]
    src_arr = src.split("/")
    filename = src_arr[-1].split('.')[0:-1]
    doc_name = ".".join([e for e in filename])
    month = src_arr[-2]
    year = src_arr[-3]
    source_str = f"{doc_name} {month} {year}"
    return source_str


graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

prompt_text = """What are the things to be considered in invoking and proving psychological incapacity?"""
response = graph.invoke({"question": prompt_text})
# invoke is the entry point of the graph passing a dict.
print(f"Question: {prompt_text}\n\n\n")
print(response["answer"])
