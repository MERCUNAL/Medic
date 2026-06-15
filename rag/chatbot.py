import pandas as pd
import time
from langchain_chroma import Chroma
import json
from langchain_core.documents import Document
from docx import Document as DocxDocument
import os
from dotenv import load_dotenv
from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI
)
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder
)
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    AnyMessage
)
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated
import streamlit as st
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


def load_vector_store():

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=GOOGLE_API_KEY
    )

    persist_directory = "./chroma_db_new"

    # LOAD CHROMADB
    vector_store = Chroma(
        collection_name="medical_data",
        embedding_function=embeddings,
        persist_directory=persist_directory
    )
    # GET EXISTING IDS
    existing = vector_store.get()

    existing_ids = set(existing["ids"])

    documents = []
    ids = []
    print(sorted(existing_ids))
    
    # LOAD EXCEL
    from pathlib import Path
    import pandas as pd
    BASE_DIR = Path(__file__).resolve().parent.parent

    excel_file = BASE_DIR / "documents" / "Medical_list_with_specs.csv"

    df = pd.read_csv(excel_file)

    for index, row in df.iterrows():
        row_dict = row.to_dict()
        chunk_text = json.dumps(row_dict)
        doc_id = f"csv_{index}"

        documents.append(
            Document(
                page_content=chunk_text,
                metadata={
                    "source": "csv",
                    "id": doc_id
                }
            )
        )
        ids.append(doc_id)
    
    # FILTER NEW DOCS
    
    new_docs = []
    new_ids = []

    for doc, doc_id in zip(documents, ids): 

        if doc_id not in existing_ids:

            new_docs.append(doc)
            new_ids.append(doc_id)

 # EMBED IN BATCHES OF 100
    batch_size = 100

    if new_docs:

        for start in range(0, len(new_docs), batch_size):

            end = start + batch_size

            batch_docs = new_docs[start:end]
            batch_ids = new_ids[start:end]

            print(
                f"Embedding batch "
                f"{start // batch_size + 1}: "
                f"{len(batch_docs)} documents"
            )

            vector_store.add_documents(
                documents=batch_docs,
                ids=batch_ids
            )

            # Wait 1 minute before the next batch
            if end < len(new_docs):
                print("Waiting 60 seconds before next batch...")
                time.sleep(60)

    else:
        print("No new CSV documents to embed")

    return vector_store


vector_store = load_vector_store()

llm = ChatGoogleGenerativeAI(
    model="models/gemini-3.1-flash-lite",
    temperature=0.3,
    google_api_key=GOOGLE_API_KEY
)

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    completed: bool
memory = MemorySaver()


prompt = ChatPromptTemplate.from_messages([
    (
        "system",
"""
You are a helpful medical and support assistant.

Communicate naturally like a chatbot.

Answer the user's question ONLY using:
1. Retrieved documents
2. Chat history

The retrieved documents may contain:
- Medical device information
- Login/signup instructions
- FAQ information

If the answer exists in the retrieved documents, answer clearly and directly.
At max present data only from 5 retrieved documents to avoid overwhelming the user.
If the products are of different types, ask the user first which type does he want information about.

If the information is not found in the retrieved documents, say:
"Sorry! I do not have that Information."

IMPORTANT:
At the end of every response, generate 3 short follow-up options the user may click.

Return your response STRICTLY in this JSON format:

{{
  "answer": "main chatbot answer",
  "options": [
    "option 1",
    "option 2",
    "option 3"
  ]
}}

Retrieved Documents:
{retrieved_docs}
"""
    ),

    MessagesPlaceholder(variable_name="chat_history"),

    (
        "human",
        "{question}"
    )
])
chain = prompt | llm

def chat(state: State):
    question = state["messages"][-1].content
    retrieved_docs = vector_store.similarity_search(
        question,
        k=7
    )
    response = chain.invoke({
        "retrieved_docs": retrieved_docs,
        "question": question,
        "chat_history": state["messages"]
    })
    return {
        "messages": [AIMessage(content=response.content)],
        "completed": True
    }


graph_builder = StateGraph(State)
graph_builder.add_node("chat", chat)
graph_builder.add_edge(START, "chat")
graph_builder.add_edge("chat", END)
graph = graph_builder.compile(
    checkpointer=memory
)

def get_response(user_input, thread_id):
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }
    result = graph.invoke(
        {
            "messages": [
                HumanMessage(content=user_input)
            ]
        },
        config=config
    )
    # GET LAST MESSAGE
    raw_response = result["messages"][-1].content
    # HANDLE GEMINI RESPONSE FORMAT
    if isinstance(raw_response, list):

        raw_response = raw_response[0]["text"]
    # PARSE JSON
    try:
        parsed = json.loads(raw_response)
        answer = parsed.get("answer", "")
        options = parsed.get("options", [])
        return answer, options

    except Exception as e:
        print("JSON PARSE ERROR:", e)
        return raw_response, []

