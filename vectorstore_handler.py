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

embedding_model = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key = GOOGLE_API_KEY
)

persist_directory = "./chroma_db"
collection_name = "my_collection"

vectorstore = Chroma(
    collection_name=collection_name,
    embedding_function=embedding_model,
    persist_directory=persist_directory
)

documents_file = "documents.json"
documents: list[Document] = []

def save_documents(docs: list[Document]):
    with open(documents_file, "w") as f:
        json_docs = [{"page_content": d.page_content, "metadata": d.metadata} for d in docs]
        json.dump(json_docs, f)

def load_documents():
    global documents
    if os.path.exists(documents_file):
        with open(documents_file, "r") as f:
            try:
                json_docs = json.load(f)
                documents = [Document(page_content=d["page_content"], metadata=d["metadata"]) for d in json_docs]
            except json.JSONDecodeError:
                documents = []
    return documents

# Load documents on module import
load_documents()

def create_and_store_embeddings(chunks):
    global documents
    # Start fresh for this upload logic if we want to replace or just append
    # If appending, we do: new_docs = [] instead of clearing documents
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
        documents.append(doc)
        
    save_documents(documents)
    BATCH_SIZE = 80  # safely under 100 RPM limit
    total_batches = math.ceil(len(new_docs) / BATCH_SIZE)

    for i in range(total_batches):
        batch = new_docs[i * BATCH_SIZE : (i + 1) * BATCH_SIZE]
        vectorstore.add_documents(batch)
        
        # wait between batches, skip delay after last batch
        if i < total_batches - 1:
            print(f"Batch {i+1}/{total_batches} embedded, waiting 60s for rate limit...")
            time.sleep(60)