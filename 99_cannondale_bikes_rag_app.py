# BUSINESS SCIENCE UNIVERSITY
# PYTHON FOR GENERATIVE AI COURSE
# RETRIEVAL-AUGMENTED GENERATION (RAG)
# ***

# OPENAI CODEX:

# Take this file, 06_product_expert_streamlit_03.py and make a copy of it as 07_cannondale_bikes_rag_app.py and update the text for this agent I'm getting ready to build. Don't change how the app works other than updating the text for Cannondale Bike Products.

# ***


# streamlit run path_to_app.py

# Chat Q&A Framework for RAG Apps
# GOAL: CONNECT MESSAGE CONTEXT (MEMORY) WITH RAG

# Key Modifications:
# 1. Persistent Chat History: Utilizing Streamlit's session state, this setup remembers past messages across reruns of the app. Each user interaction and the corresponding assistant response are appended to a message list.
# 2. Using Chat Components for Display: Each message, whether from the user or the AI assistant, is displayed within a st.chat_message context, clearly distinguishing between the participants.


# Imports 

from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# * New: History Aware Retriever
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

import streamlit as st
import yaml
import os

# Key Parameters
VECTOR_DATABASE = "data/products_vectorstore.db"
EMBEDDING_MODEL = "text-embedding-ada-002"
LLM_MODEL = "gpt-4o-mini"
# LLM_MODEL = "gpt-5.4-mini"

# Load the API Key securely
os.environ["OPENAI_API_KEY"] = yaml.safe_load(open('../credentials.yml'))['openai']

# * Page Setup

# Initialize the Streamlit app
st.set_page_config(page_title="Cannondale Bike Product Assistant")
st.title("Cannondale Bike Product Assistant")

with st.expander("I'm a Cannondale bike expert copilot that can answer detailed spec, fit, and availability questions. (see example questions)"):
    st.markdown(
        """
        - What are the key differences between the Synapse and the SuperSix EVO?
        - Which Cannondale gravel bikes come with carbon frames and electronic shifting?
        - What frame size fits a 5'10" rider for a Cannondale Synapse?
        - How does the Topstone Carbon compare to the Topstone Alloy for multi-surface rides?
        - What is the MSRP of the Cannondale Scalpel 2?
        - Which Cannondale e-bikes include removable batteries?
        
        #### SOLVED: Added Memory
        - Turn that last bike comparison into a table.
        """
    )

# * NEW: Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
if len(msgs.messages) == 0:
    msgs.add_ai_message("How can I help you with Cannondale bikes today?")


def create_rag_chain():
    
    embedding_function = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        # api_key=api_key,
        chunk_size=500,
    )
    vectorstore = Chroma(
        persist_directory=VECTOR_DATABASE,
        embedding_function=embedding_function
    )
    
    retriever = vectorstore.as_retriever()      
    
    llm = ChatOpenAI(
        model=LLM_MODEL,
        use_responses_api=True,
    )
    # llm = ChatOpenAI(
    #     model="gpt-5.4-mini",
    #     use_responses_api=True,
    #     reasoning={"effort": "none"},
    # )

    # * NEW: COMBINE CHAT HISTORY WITH RAG RETREIVER
    # * 1. Contextualize question: Integrates RAG
    contextualize_q_system_prompt = """Given a chat history and the latest user question \
    which might reference context in the chat history, formulate a standalone question \
    which can be understood without the chat history. Do NOT answer the question, \
    just reformulate it if needed and otherwise return it as is."""
    
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

    # * 2. Answer question based on Chat Context
    qa_system_prompt = """You are an assistant for question-answering tasks. \
    Use the following pieces of retrieved context to answer the question. \
    If you don't know the answer, just say that you don't know. \
    Use three sentences maximum and keep the answer concise.\

    {context}"""
    
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ])
    
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    
    # * Combine both RAG + Chat Message History
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    return RunnableWithMessageHistory(
        rag_chain,
        lambda session_id: msgs,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

rag_chain = create_rag_chain()

# Render current messages from StreamlitChatMessageHistory
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.text)

if question := st.chat_input("Ask your Cannondale bike question here:", key="query_input"):
    with st.spinner("Thinking..."):
        st.chat_message("human").write(question)     
           
        response = rag_chain.invoke(
            {"input": question}, 
            config={
                "configurable": {"session_id": "any"}
            },
        )
        # Debug response
        # print(response)
        # print("\n")
  
        st.chat_message("ai").write(response['answer'])
