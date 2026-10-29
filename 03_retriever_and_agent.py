# BUSINESS SCIENCE UNIVERSITY
# PYTHON FOR GENERATIVE AI COURSE
# RETRIEVAL-AUGMENTED GENERATION (RAG)
# ***

# Goals: Intro to ... 
# - Document Retrieval
# - Augmenting LLMs with the Product Expert Information (CONTEXT)... i.e. Creating Domain Expert Agent from a Generic LLM Model

# LIBRARIES 

# VectorStores & Text Embeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# RAG 
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Common
import yaml
import os

from pprint import pprint
from IPython.display import Markdown

# Key Parameters
VECTOR_DATABASE = "data/products_vectorstore.db"
EMBEDDING_MODEL = "text-embedding-ada-002"
# LLM_MODEL       = "gpt-4o-mini"
LLM_MODEL       = "gpt-6-luna"

# OPENAI_API_KEY

os.environ['OPENAI_API_KEY'] = yaml.safe_load(open('../credentials.yml'))['openai']

# * 1.0 CREATE A RETRIEVER FROM THE VECTORSTORE 

# Initialize the embedding function
embedding_function = OpenAIEmbeddings(
    model=EMBEDDING_MODEL,
)

# Connect to the vector store
vectorstore = Chroma(
    persist_directory=VECTOR_DATABASE,
    embedding_function=embedding_function
)

# Create a Retriever
retriever = vectorstore.as_retriever()
# retriever = vectorstore.as_retriever(search_kwargs={"k": 5}) # k = number of documents to retrieve

retriever

# How the retriever works
retriever.invoke("What is in the AI Bootcamp?")


# * 2.0 USE THE RETRIEVER TO AUGMENT AN LLM

# * Prompt template 

template = """Answer the question based only on the following context:
{context}

# ADDITIONAL INSTRUCTIONS:
If a student is on the fence about enrolling in the program, highlight the benefits of joining the program.

Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

prompt

# * Generic LLM Specification

# model = ChatOpenAI(
#     model=LLM_MODEL,
#     use_responses_api=True,
# )
model = ChatOpenAI(
    model=LLM_MODEL, # adjust for better performance models like gpt-5.4
    use_responses_api=True,
    reasoning={"effort": "none"}, # adjust this to "medium" or "high" for more complex reasoning tasks
)

model

result = model.invoke("What is the color of the sky? Answer in 1 word.")

result

result.content

result.content[0]['text']

result.text

# * Combine with Lang Chain Expression Language (LCEL)
#   - Context: Give it access to the retriever
#   - Question: Provide the user question as a pass through from the invoke method
#   - Use LCEL to add a prompt template, model spec, and output parsing

rag_agent = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

rag_agent

# * Try it out:

# * Baseline (Generic LLM)
result_baseline = model.invoke("What is inside the AI Bootcamp and what is the price? Cite your sources and URL.")

Markdown(result_baseline.text)

# * RAG Agent (Unstructured Domain Expert LLM)
result = rag_agent.invoke("What is inside the AI Bootcamp and what is the price? Cite your sources and URL.")

Markdown(result)

# * AI Bootcamp Test

result = rag_agent.invoke("Is the AI Bootcamp worth it?")

Markdown(result)

# CONCLUSION:
# - The RAG (Retrieval-Augmented Generation) approach significantly improves the LLM's ability to answer questions by providing it with relevant context from the vector store. This allows for more accurate and context-aware responses.
# - This is one way to build domain-specific knowledge into a generative model, enhancing its performance on specialized tasks.
# - IMPORTANT: Many companies need this.
