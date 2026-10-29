# CHALLENGE 1 - STEP 3: STREAMLIT WEB APP WITH RAG + CHAT MEMORY
# Run from the project root with:
#   streamlit run challenges/challenge_01_statistical_learning_pdf/challenge_01_app.py

from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

import streamlit as st
import yaml
import os

# --- Config -------------------------------------------------------------
# Resolve paths from this file's location so the app runs from any working directory
APP_DIR      = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, "..", ".."))

VECTOR_DATABASE = os.path.join(APP_DIR, "data", "islp_vectorstore.db")
EMBEDDING_MODEL = "text-embedding-ada-002"
LLM_MODEL       = "gpt-4o-mini"

# API key: Streamlit Cloud secrets first, then env var, then local credentials.yml
CREDENTIALS_FILE = os.path.join(PROJECT_ROOT, "credentials.yml")
try:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
except Exception:
    if "OPENAI_API_KEY" not in os.environ and os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE) as f:
            os.environ["OPENAI_API_KEY"] = yaml.safe_load(f)["openai"]

if not os.environ.get("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY not found. Add it under App settings → Secrets.")
    st.stop()

# --- Page setup ---------------------------------------------------------
st.set_page_config(page_title="Your Data Science Reference Copilot", layout="wide")
st.title("Your Data Science Reference Copilot")

with st.expander("Built on the Introduction to Statistical Learning (ISLP) textbook. Try asking:"):
    st.markdown(
        """
        - What is the bias-variance trade-off?
        - How does ridge regression differ from lasso?
        - Explain principal component analysis in simple terms.
        - What are the top 3 things needed to do PCA?
        - Summarize the chapter on tree-based methods.
        """
    )

# --- Chat memory --------------------------------------------------------
msgs = StreamlitChatMessageHistory(key="langchain_messages")
if len(msgs.messages) == 0:
    msgs.add_ai_message("How can I help you with Introduction to Statistical Learning?")

view_messages = st.expander("View the message contents in session state")


def create_rag_chain():
    # 1) Reconnect to the vector store we built in step 2
    embedding_function = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        chunk_size=500,
    )
    vectorstore = Chroma(
        persist_directory=VECTOR_DATABASE,
        embedding_function=embedding_function,
    )
    retriever = vectorstore.as_retriever()

    # 2) The chat model that will answer
    llm = ChatOpenAI(
        model=LLM_MODEL,
        use_responses_api=True,
    )

    # 3) History-aware retriever: rewrites a follow-up like "and in R?"
    #    into a standalone question before searching the vector store.
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question which might "
        "reference context in the chat history, formulate a standalone "
        "question which can be understood without the chat history. "
        "Do NOT answer the question, just reformulate it if needed and "
        "otherwise return it as is."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    # 4) Answer prompt: stuffs retrieved chunks into {context}
    qa_system_prompt = (
        "You are an assistant for data-science question-answering tasks "
        "grounded in the Introduction to Statistical Learning with Python "
        "textbook. Use the following pieces of retrieved context to answer. "
        "If you don't know the answer, just say that you don't know. "
        "Use three sentences maximum and keep the answer concise.\n\n"
        "{context}"
    )
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    # 5) Combine retriever + answer chain, then wrap with memory
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    return RunnableWithMessageHistory(
        rag_chain,
        lambda session_id: msgs,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )


rag_chain = create_rag_chain()

# --- Render chat history ------------------------------------------------
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.text)

# --- User input + response ---------------------------------------------
if question := st.chat_input("Ask a statistical learning question:", key="query_input"):
    with st.spinner("Thinking..."):
        st.chat_message("human").write(question)
        response = rag_chain.invoke(
            {"input": question},
            config={"configurable": {"session_id": "any"}},
        )
        st.chat_message("ai").write(response["answer"])

# --- Debug panel --------------------------------------------------------
with view_messages:
    view_messages.json(st.session_state.langchain_messages)
