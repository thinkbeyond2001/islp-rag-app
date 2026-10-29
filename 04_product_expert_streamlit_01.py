# BUSINESS SCIENCE UNIVERSITY
# PYTHON FOR GENERATIVE AI COURSE
# RETRIEVAL-AUGMENTED GENERATION (RAG)
# ***

# streamlit run path_to_app.py

# Goal: Take what you've learned and show how to put it into a simple Q&A streamlit app.

# APP #1: SINGLE Q&A
# - GREAT FOR SIMPLE 1-OFF TASKS (E.G. WRITE ME AN EMAIL)
# - PROBLEM: NO CHAT CAPABILITY

# Imports

from langchain_chroma import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

import yaml
import os

# * New: Add streamlit
import streamlit as st

# Key Parameters
VECTOR_DATABASE = "data/products_vectorstore.db"
EMBEDDING_MODEL = "text-embedding-ada-002"
# LLM_MODEL       = "gpt-4o-mini"
LLM_MODEL       = "gpt-6-luna"

# *New: Initialize the Streamlit app
st.set_page_config(
    page_title="Your Product Assistant", 
    layout="wide"
)

# Load the API Key securely
os.environ["OPENAI_API_KEY"] = yaml.safe_load(open('../credentials.yml'))['openai']

# Function to create the processing rag_agent
def create_rag_agent():
    embedding_function = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
    )

    vectorstore = Chroma(
        persist_directory=VECTOR_DATABASE,
        embedding_function=embedding_function
    )

    retriever = vectorstore.as_retriever()

    template = """Answer the question based only on the following context:
    {context}
    
    If a student is on the fence about enrolling in the AI Bootcamp, highlight the benefits of joining the program.

    Question: {question}
    """

    prompt = ChatPromptTemplate.from_template(template)

    model = ChatOpenAI(
        model=LLM_MODEL,
        use_responses_api=True,
        reasoning={"effort": "none"},
    )
    # model = ChatOpenAI(
    #     model="gpt-5.4-mini",
    #     use_responses_api=True,
    #     reasoning={"effort": "none"},
    # )

    rag_agent = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | model
        | StrOutputParser()
    )
    return rag_agent

rag_agent = create_rag_agent()

# Main app interface
st.title("Your Product Expert Copilot")

with st.expander("I'm a complete product expert copilot that can help answer questions about products for Business Science University. (see example questions)"):
    st.markdown(
        """
        - What are the key features of the 8-Week AI Bootcamp?
        - How long will it take to complete the 8-Week AI Bootcamp?
        - Estimate the time to complete the 8-Week AI Bootcamp if I dedicate 10 hours per week to my studies.
        - What are the prerequisites for enrolling in the 8-Week AI Bootcamp?        
        - What is the price of AI Bootcamp?
        - What is the website for AI Bootcamp?

        #### Problem: No conversation history
        """
    )

# Layout for input and output
col1, col2 = st.columns(2)

with col1:
    st.header("How can I help you?")    
    question = st.text_area("Enter your Product question here:", height=300)
    submit_button = st.button("Submit")

with col2:
    st.header("AI Generated Answer")
    if submit_button and question:
        # Process the question through the rag_agent
        with st.spinner("Processing your question..."):
            try:
                # Process the question through the rag_agent                
                answer = rag_agent.invoke(question)
                st.write(answer)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        
        st.write("Your answer will appear here.")

