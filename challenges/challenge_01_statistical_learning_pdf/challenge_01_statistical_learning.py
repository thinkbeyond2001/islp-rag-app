# BUSINESS SCIENCE UNIVERSITY
# PYTHON FOR GENERATIVE AI COURSE
# RETRIEVAL-AUGMENTED GENERATION (RAG)
# ***

# CHALLENGE 1: CREATE A DATA SCIENCE EXPERT USING THE INTRODUCTION TO STATISTICAL LEARNING WITH PYTHON PDF

# DIFFICULTY: BEGINNER

# SPECIFIC ACTIONS:
#  1. USE PDF LOADER TO LOAD THE PDF AND PROCESS THE TEXT
#  2. CREATE A VECTOR DATABASE TO STORE KNOWLEDGE FROM THE BOOK'S PDF
#  3. CREATE A WEB APP THAT INCORPORATES Q&A AND CHAT MEMORY


# * HINT: You will need to using chunking when processing the PDF due to its size. See the lanchain text splitters documentation for more details.

# >>> CHANGE LOG (debug fixes) -------------------------------------------------
# Everything else in this file is unchanged from the original.
#
# 1. CHANGED IN THIS FILE: "LOAD INTO THE VECTOR DATABASE" section
#    (search for ">>> CHANGED"). The vector store is now built when it is EMPTY,
#    not when its folder is missing. A failed run (e.g. bad API key) left an empty
#    folder behind, so the old check skipped the build forever -> "stored: 0".
#
# 2. NOT IN THIS FILE: ..\.vscode\settings.json (outer workspace folder), so the
#    VS Code "Run" button (Code Runner) works:
#    - ModuleNotFoundError: No module named 'pypdf'
#        Code Runner used the base Anaconda python. It now uses the
#        ds4b_301p_dev_langchain_latest env, where pypdf is installed.
#    - credentials.yml / PDF not found (would have been the next error)
#        Code Runner now runs from the project root (code-runner.cwd), which the
#        relative paths in this script expect.
#    - UnicodeEncodeError: 'charmap' codec can't encode character '−'
#        Output to the VS Code panel used Windows cp1252, which can't print the
#        book's math symbols (−, λ). Python now runs with "-X utf8".
#
# 3. STILL TO DO (not a code bug): credentials.yml holds the placeholder
#    "YOUR_OPENAI_API_KEY", which causes the 401 error at the embedding step.
#    Replace it with your real OpenAI key.
# <<< END CHANGE LOG -----------------------------------------------------------

# LIBRARIES ----

import copy
import glob
import joblib
import os
import statistics
import yaml
import pypdf
from datetime import datetime
#pip install pypdf
from pypdf import PdfReader
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# OPENAI API SETUP (run from the project root)
os.environ['OPENAI_API_KEY'] = yaml.safe_load(open('credentials.yml'))['openai']

MODEL_EMBEDDING = 'text-embedding-ada-002'
DATA_DIR = "challenges/challenge_01_statistical_learning_pdf/data"
VECTORSTORE_PATH = f"{DATA_DIR}/islp_vectorstore.db"


#  1. USE PDF LOADER TO LOAD THE PDF AND PROCESS THE TEXT ----

PDF_PATH = "challenges/challenge_01_statistical_learning_pdf/pdf/ISLP_website.pdf"

# Load: one Document per page
loader = PyPDFLoader(PDF_PATH)
documents = loader.load()
print(f"Loaded {len(documents)} pages")

# Trim: drop the garbled cover, dedication, preface and table of contents
# Also drop the book's index at the end (starts at page label 603 = index 602)
documents = documents[11:602]
# documents = documents[2:4] + documents[11:602]   # use this instead to keep the preface
print(f"Pages after trimming: {len(documents)}")

# Split: chunk the pages
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)

chunks = text_splitter.split_documents(documents)
print(f"Split {len(documents)} pages into {len(chunks)} chunks")

# Drop plot junk (rug plots extracted as rows of "|||||", unmapped font glyphs like "/g1/g4")
chunks = [
    c for c in chunks
    if c.page_content.count("|") / len(c.page_content) < 0.2
    and c.page_content.count("/g") < 5
]
print(f"After removing junk chunks: {len(chunks)}")


# CHECKS BEFORE LOADING INTO THE VECTOR DATABASE ----

lengths = [len(c.page_content) for c in chunks]
print("chunks:", len(chunks))
print("mean:", statistics.mean(lengths), "median:", statistics.median(lengths))
print("min:", min(lengths), "max:", max(lengths))

print(chunks[0].metadata)
print(chunks[0].page_content[:300])

# Tiny chunks (usually headers or lone figure labels)
tiny = [c for c in chunks if len(c.page_content) < 100]
print("tiny chunks (<100 chars):", len(tiny))
for c in tiny[:5]:
    print(c.metadata["page_label"], repr(c.page_content))

# Garbled chunks (mostly non-letter characters, e.g. bad font encoding)
def looks_garbled(text):
    letters = sum(ch.isalpha() or ch.isspace() for ch in text)
    return letters / max(len(text), 1) < 0.6

garbled = [c for c in chunks if looks_garbled(c.page_content)]
print("suspicious chunks:", len(garbled))
for c in garbled[:5]:
    print(c.metadata["page_label"], c.page_content[:150].replace("\n", " "))

# Metadata present on every chunk
assert all("page_label" in c.metadata and "source" in c.metadata for c in chunks)

# First and last chunks
print("FIRST:", chunks[0].page_content[:200].replace("\n", " "))
print("LAST:", chunks[-1].page_content[:200].replace("\n", " "))

# Last pages: check whether the book's index is at the end
for i in range(len(documents) - 15, len(documents)):
    print(i, documents[i].metadata["page_label"], documents[i].page_content[:80].replace("\n", " "))


## ADDING METADATA: CHAPTER AND SECTION FROM THE PDF BOOKMARKS ----

reader = PdfReader(PDF_PATH)

def flatten_outline(items, level=0):
    """Flatten the nested bookmark tree into (start_page_index, level, title)."""
    flat = []
    for item in items:
        if isinstance(item, list):
            flat.extend(flatten_outline(item, level + 1))
        else:
            flat.append((reader.get_destination_page_number(item), level, item.title.strip()))
    return flat

outline = flatten_outline(reader.outline)
chapters = [(p, t) for p, lvl, t in outline if lvl == 0]
sections = [(p, t) for p, lvl, t in outline if lvl == 1]

def title_for_page(entries, page):
    """Title of the last bookmark that starts on or before this page."""
    title = None
    for start, t in entries:
        if start <= page:
            title = t
        else:
            break
    return title

for c in chunks:
    c.metadata["chapter"] = title_for_page(chapters, c.metadata["page"])
    c.metadata["section"] = title_for_page(sections, c.metadata["page"])

# Spot check
for c in (chunks[0], chunks[800], chunks[-1]):
    print(c.metadata["page_label"], "|", c.metadata["chapter"], "|", c.metadata["section"])


page_chunks = [c for c in chunks if c.metadata["page_label"] == "260"]
for c in page_chunks:
    print(c.metadata["chapter"], "|", c.metadata["section"])
    print(c.page_content[:200].replace("\n", " "), "\n")


#  2. CREATE A VECTOR DATABASE TO STORE KNOWLEDGE FROM THE BOOK'S PDF ----

# Add chapter and section to the page content so they are embedded with the text
chunks_with_metadata = copy.deepcopy(chunks)

for chunk in chunks_with_metadata:
    chapter = chunk.metadata.get("chapter", "Unknown Chapter")
    section = chunk.metadata.get("section", "Unknown Section")
    chunk.page_content = f"Chapter: {chapter}\nSection: {section}\n\n{chunk.page_content}"

print(chunks_with_metadata[800].page_content[:300])


# SAVE THE PROCESSED CHUNKS TO A NEW PKL FILE (never overwrites an existing one) ----

os.makedirs(DATA_DIR, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
chunks_pkl_path = f"{DATA_DIR}/islp_chunks_{timestamp}.pkl"

assert not os.path.exists(chunks_pkl_path), f"{chunks_pkl_path} already exists"
joblib.dump(chunks_with_metadata, chunks_pkl_path)
print(f"Saved {len(chunks_with_metadata)} chunks to {chunks_pkl_path}")


# LOAD THE CHUNKS FROM THE LATEST PKL FILE ----

latest_pkl_path = max(glob.glob(f"{DATA_DIR}/islp_chunks_*.pkl"))  # timestamps sort alphabetically
documents_for_vectorstore = joblib.load(latest_pkl_path)
print(f"Loaded {len(documents_for_vectorstore)} chunks from {latest_pkl_path}")


# LOAD INTO THE VECTOR DATABASE ----

# NOTE: The embedding model selected needs to be used every time you access the Vector Store
embedding_function = OpenAIEmbeddings(
    model=MODEL_EMBEDDING,
)

# >>> CHANGED (debug fix) ------------------------------------------------------
# BEFORE:
#   if not os.path.exists(VECTORSTORE_PATH):
#       Chroma.from_documents(documents_for_vectorstore, embedding=embedding_function,
#                             persist_directory=VECTORSTORE_PATH)
#   vectorstore = Chroma(embedding_function=embedding_function,
#                        persist_directory=VECTORSTORE_PATH)
#
# WHY: Chroma creates the folder BEFORE embedding. If embedding fails (e.g. bad
# API key -> 401), an empty folder is left behind. The old folder-exists check
# then skipped the build on every later run, leaving an empty store (stored: 0).
# Now we check whether the store has any documents instead of whether the folder exists.

# Connect to the Vector Store (creates the folder if it does not exist)
vectorstore = Chroma(
    embedding_function=embedding_function,
    persist_directory=VECTORSTORE_PATH,
)

# Embed the chunks only if the store is empty (first run, or a previous run failed
# part-way and left an empty folder); delete the folder to force a rebuild
if vectorstore._collection.count() == 0:
    vectorstore.add_documents(documents_for_vectorstore)
# <<< END CHANGED ---------------------------------------------------------------

print("stored:", vectorstore._collection.count())


# TEST RETRIEVAL ----

for question in ["What is the bias-variance trade-off?", "How does ridge regression differ from lasso?"]:
    print("\nQUESTION:", question)
    for r in vectorstore.similarity_search(query=question, k=4):
        print(f"  p.{r.metadata['page_label']} | {r.metadata['chapter']} | {r.metadata['section']}")


# =============================================================================
# TRY IT OUT:  BASELINE LLM  vs.  RAG AGENT
# =============================================================================
# Compare how a plain LLM answers vs. a RAG agent grounded in the ISLP textbook.
# Pattern taken from 03_retriever_and_agent.py.

from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

LLM_MODEL = "gpt-4o-mini"   # cheap + fast; swap for "gpt-5.4-mini" if you prefer

# --- 1) Build a plain LLM (no context, no retrieval) ------------------------
baseline_llm = ChatOpenAI(model=LLM_MODEL)

# --- 2) Build a RAG agent on top of the ISLP vector store -------------------
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

rag_prompt = ChatPromptTemplate.from_template(
    """Answer the question using ONLY the following context from the
Introduction to Statistical Learning (ISLP) textbook.
If the context does not contain the answer, say so.
Cite the chapter and page where possible.

Context:
{context}

Question: {question}
"""
)

def format_docs(docs):
    """Join retrieved chunks into one string the LLM can read, with citations."""
    return "\n\n---\n\n".join(
        f"[p.{d.metadata.get('page_label')} | {d.metadata.get('chapter')} | "
        f"{d.metadata.get('section')}]\n{d.page_content}"
        for d in docs
    )

rag_agent = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | rag_prompt
    | baseline_llm
    | StrOutputParser()
)

# --- 3) Ask the same questions to both --------------------------------------
test_questions = [
    "What is the bias-variance trade-off?",
    "How does ridge regression differ from lasso? Cite the chapter and page.",
    "What are the top 3 things needed to do principal component analysis?",
    "According to ISLP, when should you prefer tree-based methods over linear models?",
]

for q in test_questions:
    print("\n" + "=" * 80)
    print("QUESTION:", q)
    print("=" * 80)

    print("\n--- BASELINE LLM (no textbook, answers from general knowledge) ---")
    print(baseline_llm.invoke(q).content)

    print("\n--- RAG AGENT (grounded in ISLP chunks) ---")
    print(rag_agent.invoke(q))

# WHAT TO LOOK FOR WHEN YOU READ THE OUTPUT:
# - The baseline answers tend to be generic and uncited; the model is talking
#   from whatever it saw during training.
# - The RAG answers quote the book's own wording and include chapter / page
#   citations, because format_docs embeds those into the context the LLM sees.
# - For a very ISLP-specific question (e.g. "According to ISLP, when...") the
#   baseline often hedges or hallucinates while the RAG agent stays grounded.


# -----------------------------------------------------------------------------
# OPTIONAL: inspect what the retriever actually hands to the LLM
# -----------------------------------------------------------------------------
# Uncomment to peek at the exact context string for one question:
#
# q = "How does ridge regression differ from lasso?"
# retrieved = retriever.invoke(q)
# print(format_docs(retrieved))


#  3. CREATE A WEB APP THAT INCORPORATES Q&A AND CHAT MEMORY ----
#
# The code below is a Streamlit app. Save it as its own file (for example
# `challenge_01_app.py`) and run it from the project root with:
#
#     streamlit run challenges/challenge_01_statistical_learning_pdf/challenge_01_app.py
#
# It follows the same pattern as `06_product_expert_streamlit_03.py`, but
# points at the ISLP vector store built above instead of the products store.
#
# ---------------------------------------------------------------------------
# from langchain_chroma import Chroma
# from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_core.runnables.history import RunnableWithMessageHistory
# from langchain_community.chat_message_histories import StreamlitChatMessageHistory
# from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
# from langchain_classic.chains.combine_documents import create_stuff_documents_chain
#
# import streamlit as st
# import yaml
# import os
#
# # --- Config -------------------------------------------------------------
# VECTOR_DATABASE = "challenges/challenge_01_statistical_learning_pdf/data/islp_vectorstore.db"
# EMBEDDING_MODEL = "text-embedding-ada-002"
# LLM_MODEL       = "gpt-4o-mini"   # or "gpt-5.4-mini"
#
# os.environ["OPENAI_API_KEY"] = yaml.safe_load(open("credentials.yml"))["openai"]
#
# # --- Page setup ---------------------------------------------------------
# st.set_page_config(page_title="Your Data Science Reference Copilot", layout="wide")
# st.title("Your Data Science Reference Copilot")
#
# with st.expander("I'm a data science copilot built on the ISLP textbook. Try asking:"):
#     st.markdown(
#         """
#         - What is the bias-variance trade-off?
#         - How does ridge regression differ from lasso?
#         - Explain principal component analysis in simple terms.
#         - What are the top 3 things needed to do PCA?
#         - Summarize the chapter on tree-based methods.
#         """
#     )
#
# # --- Chat memory --------------------------------------------------------
# # StreamlitChatMessageHistory stores messages in st.session_state so they
# # survive Streamlit's reruns on every user interaction.
# msgs = StreamlitChatMessageHistory(key="langchain_messages")
# if len(msgs.messages) == 0:
#     msgs.add_ai_message("How can I help you with Introduction to Statistical Learning?")
#
# view_messages = st.expander("View the message contents in session state")
#
# # --- RAG chain builder --------------------------------------------------
# def create_rag_chain():
#     # 1) Reconnect to the vector store we built above
#     embedding_function = OpenAIEmbeddings(
#         model=EMBEDDING_MODEL,
#         chunk_size=500,
#     )
#     vectorstore = Chroma(
#         persist_directory=VECTOR_DATABASE,
#         embedding_function=embedding_function,
#     )
#     retriever = vectorstore.as_retriever()
#
#     # 2) The chat model that will answer the user
#     llm = ChatOpenAI(
#         model=LLM_MODEL,
#         use_responses_api=True,
#     )
#
#     # 3) History-aware retriever: rewrites a follow-up like "and in R?" into
#     #    a standalone question before searching the vector store.
#     contextualize_q_system_prompt = (
#         "Given a chat history and the latest user question which might "
#         "reference context in the chat history, formulate a standalone "
#         "question which can be understood without the chat history. "
#         "Do NOT answer the question, just reformulate it if needed and "
#         "otherwise return it as is."
#     )
#     contextualize_q_prompt = ChatPromptTemplate.from_messages([
#         ("system", contextualize_q_system_prompt),
#         MessagesPlaceholder("chat_history"),
#         ("human", "{input}"),
#     ])
#     history_aware_retriever = create_history_aware_retriever(
#         llm, retriever, contextualize_q_prompt
#     )
#
#     # 4) Answer prompt: stuffs the retrieved chunks into {context}
#     qa_system_prompt = (
#         "You are an assistant for data-science question-answering tasks "
#         "grounded in the Introduction to Statistical Learning with Python "
#         "textbook. Use the following pieces of retrieved context to answer. "
#         "If you don't know the answer, just say that you don't know. "
#         "Use three sentences maximum and keep the answer concise.\n\n"
#         "{context}"
#     )
#     qa_prompt = ChatPromptTemplate.from_messages([
#         ("system", qa_system_prompt),
#         MessagesPlaceholder("chat_history"),
#         ("human", "{input}"),
#     ])
#     question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
#
#     # 5) Combine retriever + answer chain, then wrap with memory
#     rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
#
#     return RunnableWithMessageHistory(
#         rag_chain,
#         lambda session_id: msgs,
#         input_messages_key="input",
#         history_messages_key="chat_history",
#         output_messages_key="answer",
#     )
#
# rag_chain = create_rag_chain()
#
# # --- Render chat history ------------------------------------------------
# for msg in msgs.messages:
#     st.chat_message(msg.type).write(msg.text)
#
# # --- User input + response ---------------------------------------------
# if question := st.chat_input("Ask a statistical learning question:", key="query_input"):
#     with st.spinner("Thinking..."):
#         st.chat_message("human").write(question)
#         response = rag_chain.invoke(
#             {"input": question},
#             config={"configurable": {"session_id": "any"}},
#         )
#         st.chat_message("ai").write(response["answer"])
#
# # --- Debug panel --------------------------------------------------------
# with view_messages:
#     view_messages.json(st.session_state.langchain_messages)
