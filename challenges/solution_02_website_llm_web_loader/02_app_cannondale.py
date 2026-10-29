# BUSINESS SCIENCE STUDENT EXAMPLES
# COHORT 4: Brandyn Adderley and Heinrich Muller
# Streamlit Web App with Image Support


# streamlit run path_to_this_file.py



# Imports 
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
import streamlit as st
import yaml
import os
import requests  # For validating image URLs
import re 

# Key Parameters
RAG_DATABASE = "challenges/solution_02_website_llm_web_loader/data/chroma_cannondale.db"
EMBEDDING_MODEL = "text-embedding-ada-002"
LLM_MODEL = "gpt-4o-mini"
# LLM_MODEL = "gpt-5.4-mini"

# Initialize the Streamlit app
st.set_page_config(page_title="Your Cannondale Bike Recommendation AI", layout="wide")
st.title("Your Cannondale Bike Recommendation AI")

with st.expander("I'm a complete Cannondale bike expert copilot that can help answer questions about products for Cannondale. (see example questions)"):
    st.markdown(
        """
        - What are the key features of the Cannondale SuperSix EVO?
        - What is a good mountain bike under $1000. Describe it to me.
        - Put the key features in a table for the Trail 7.1
        - Are there any high end mountain bikes that sell for over $10,000?
        """
    )

# Load the API Key securely
os.environ["OPENAI_API_KEY"] = yaml.safe_load(open('../credentials.yml'))['openai']

# Set up chat history memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
if len(msgs.messages) == 0:
    msgs.add_ai_message("How can I help you with bike models? Ask about a specific model to see its details and image!")

# Debugging expander for session messages
view_messages = st.expander("View the message contents in session state")

# --- Helpers ---
def is_valid_image_url(url):
    """Check if URL is reachable and points to an image."""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200 and 'image' in response.headers.get('content-type', '').lower()
    except requests.RequestException:
        return False

def extract_url_from_text(text: str) -> str | None:
    """Extract the first http/https URL from text if present."""
    match = re.search(r'(https?://\S+)', text)
    return match.group(1) if match else None

def create_rag_chain():
    # Initialize embeddings
    embedding_function = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        chunk_size=500,
    )
    
    # Connect to vector store
    vectorstore = Chroma(
        persist_directory=RAG_DATABASE,
        embedding_function=embedding_function
    )
    
    # Create retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 1})  # Retrieve top 1 document
    
    # Initialize LLM
    llm = ChatOpenAI(
        model=LLM_MODEL,
        use_responses_api=True,
    )
    # llm = ChatOpenAI(
    #     model="gpt-5.4-mini",
    #     use_responses_api=True,
    #     reasoning={"effort": "none"},
    # )

    # Contextualize question
    contextualize_q_system_prompt = """Given a chat history and the latest user question \
    which might reference context in the chat history, formulate a standalone question \
    which can be understood without the chat history. Do NOT answer the question, \
    just reformulate it if needed and otherwise return it as is."""
    
    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    
    # Create history-aware retriever
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

    # QA system prompt
    qa_system_prompt = """You are an assistant for question-answering tasks about bike models. \
    Use the following pieces of retrieved context to answer the question concisely. \
    If an image URL is available, include it in the answer by stating 'Main Image URL: [URL]'. \
    If you don't know the answer, say so. Keep the answer to three sentences maximum.\

    {context}"""
    
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ])
    
    # Create QA chain
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    
    # Combine RAG + History
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    return RunnableWithMessageHistory(
        rag_chain,
        lambda session_id: msgs,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    ), retriever

# Create RAG chain and retriever
rag_chain, retriever = create_rag_chain()

# Render current messages
for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.text)

# Handle user input
if question := st.chat_input("Enter your question about a bike model:", key="query_input"):
    with st.spinner("Thinking..."):
        # Display user question
        st.chat_message("human").write(question)
        
        # Invoke RAG chain
        response = rag_chain.invoke(
            {"input": question}, 
            config={
                "configurable": {"session_id": "any"}
            },
        )
        
        # Get the answer
        answer = response['answer']
        
        # Display the answer
        st.chat_message("ai").write(answer)

        # Extract main image URL
        main_image_url = extract_url_from_text(answer)

        # --- Display image ---
        if main_image_url and is_valid_image_url(main_image_url):
            st.image(
                main_image_url,
                width=300
            )
        else:
            st.write("No valid image available for this bike model.")



    
