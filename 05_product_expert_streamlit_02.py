# BUSINESS SCIENCE UNIVERSITY
# PYTHON FOR GENERATIVE AI COURSE
# RETRIEVAL-AUGMENTED GENERATION (RAG)
# ***

# GOAL: ADD CHAT INTERFACE FOR CONVERSATIONAL INTERFACE

# streamlit run path_to_app.py

# APP #2: Add Chat Interface
# - Users can now have multiple questions (not limited to single submission)
# - PROBLEM: RAG and memory are not connected


# Key Modifications:
#  1. Persistent Chat History: Utilizing Streamlit's session state, this setup remembers past messages across reruns of the app. Each user interaction and the corresponding assistant response are appended to a message list.
#  2. Using Chat Components for Display: Each message, whether from the user or the AI assistant, is displayed within a st.chat_message context, clearly distinguishing between the participants.


# Libraries

from langchain_chroma import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

import yaml
import os
import streamlit as st

# Key Parameters
VECTOR_DATABASE = "data/products_vectorstore.db"
EMBEDDING_MODEL = "text-embedding-ada-002"
LLM_MODEL       = "gpt-4o-mini"
# LLM_MODEL       = "gpt-5.4-mini"

# Load the API Key securely
os.environ["OPENAI_API_KEY"] = yaml.safe_load(open('../credentials.yml'))['openai']

# Initialize the Streamlit app
st.set_page_config(page_title="Your Product Assistant", )
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
        
        #### Problem: No Memory
        - Put what you just did in a table.
        """
    )

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

# * NEW: Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "ai", "content": "How can I help you?"}]

# * NEW: Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# * NEW: Chat messages get appended as Q&A occurs in the app
if question := st.chat_input("Enter your product question here:"):
    with st.spinner("Thinking..."): 
        
        # Add user message to chat history
        st.chat_message("human").write(question)

        # Get the response from the AI model
        response = rag_agent.invoke(question)
        
        # For Debugging
        # print(response)
        # print("/n")

        # Add AI response to chat history
        st.chat_message("ai").write(response)
        
        # Append both messages to the session state
        st.session_state.messages.append({"role": "human", "content": question})
        st.session_state.messages.append({"role": "ai", "content": response})
