# BUSINESS SCIENCE UNIVERSITY
# PYTHON FOR GENERATIVE AI COURSE
# RETRIEVAL-AUGMENTED GENERATION (RAG)
# ***

# Goal: Collect Expertise on a Topic that's relevant to your business application

# WEB SCRAPING SETUP 
# ------------------------------------------------
# 1. Install required packages if needed (langchain_community for WebBaseLoader, beautifulsoup4 for parsing)
# 2. Note: Web scraping should respect website terms, robots.txt, and legal guidelines. This is for educational purposes only.


# * 1.0 LIBRARIES

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document

# Other Libraries
import pandas as pd
import joblib

import nest_asyncio # Used for asynchronously loading

from pprint import pprint
from IPython.display import Markdown


# * 2.0 WEB PAGE LOADING

# * Test out loading a single webpage
#   Resource: https://docs.langchain.com/oss/python/integrations/document_loaders/web_base

url = "https://university.business-science.io/p/4-course-bundle-machine-learning-and-web-applications-r-track-101-102-201-202a"

# Create a document loader for the website
loader = WebBaseLoader(url)

# Load the data from the website
documents = loader.load()

# list()
# list((1,2,3))

# Returns a list containing documents
documents

len(documents)

documents[0]

dict(documents[0]).keys()

pprint(documents[0].metadata)

pprint(documents[0].metadata['source'])

pprint(documents[0].page_content)

# * Load All Webpages Asynchronously
#   This will take a minute

# Get the websites
df = pd.read_csv("data/products.csv")

df['website'].tolist()

# * 2.1 Load All Webpages Asynchronously

# Create a loader
loader = WebBaseLoader(df['website'].tolist())

# * Synchronous Loading (Slower)

# Load Synchronously (Takes about 16 seconds for 13 webpages)
documents = loader.load()

# * NEW - Load Asynchronously (Takes about 2 seconds for 13 webpages)
nest_asyncio.apply()

documents = loader.aload()

# Examine documents

documents

documents[-1].metadata

pprint(documents[-1].page_content)

len(documents[-1].page_content)

# * NEW - Adding Meta TOC Document
#   Sometimes you want to add a "meta document" that contains information about the data source. Kind of like the Table of Contents for a book. 

toc_content = """
This Document Collection contains information on all products available at Business Science University. Here is a list of products included: 
"""

pprint(toc_content)

for index, row in df.iterrows():
    toc_content += f"- {row['product_id']} | {row['description']} | {row['website']}\n"  

pprint(toc_content)

Markdown(toc_content)

toc_doc = Document(
    page_content=toc_content, 
    metadata={"source": "Table of Contents"}
)

toc_doc

documents.insert(0, toc_doc)

documents[0]

# * 3.0 SAVE DOCUMENTS (CHECKPOINT)

joblib.dump(documents, "data/products.pkl")

documents = joblib.load("data/products.pkl")

documents[-1].metadata

documents[-1].page_content

documents[0].metadata
documents[0].page_content

# CONCLUSIONS
# - Successfully web-scraped and processed web pages
# - Extracted relevant content for further vectorization and similarity search
# - Added a TOC meta document to provide context about the document collection
