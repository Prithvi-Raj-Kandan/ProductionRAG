from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv
import os
import math
import time
import json

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
embedding_model = None


def get_embedding_model():
    global embedding_model
    if embedding_model is None:
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not set.")
        embedding_model = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001",
            google_api_key=GOOGLE_API_KEY
        )
    return embedding_model

user_sessions: dict[str, dict] = {}

def get_session_data(session_id: str):
    if session_id not in user_sessions:
        user_sessions[session_id] = {"documents": [], "vectorstore": None}
    return user_sessions[session_id]

def delete_session_data(session_id: str):
    if session_id in user_sessions:
        # In-memory Chroma database drops cleanly when the python object is destroyed
        del user_sessions[session_id]

def create_and_store_embeddings(chunks, session_id: str):
    session_data = get_session_data(session_id)
    new_docs = []

    for chunk in chunks:
        doc = Document(
            page_content=chunk["text"],
            metadata={
                "pdf_name": chunk["pdf_name"],
                "page_no": chunk["page_no"],
                "paragraph_no": chunk["paragraph_no"]
            }
        )
        new_docs.append(doc)
        session_data["documents"].append(doc)
        
    vectorstore = Chroma(
        collection_name=f"session_{session_id}",
        embedding_function=get_embedding_model()
    )
    session_data["vectorstore"] = vectorstore

    BATCH_SIZE = 80  
    total_batches = math.ceil(len(new_docs) / BATCH_SIZE)

    for i in range(total_batches):
        batch = new_docs[i * BATCH_SIZE : (i + 1) * BATCH_SIZE]
        vectorstore.add_documents(batch)
        if i < total_batches - 1:
            print(f"Batch {i+1}/{total_batches} embedded, waiting 60s for rate limit...")
            time.sleep(60)