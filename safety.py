from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv
import chromadb  

load_dotenv()  
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
chromadb_client = chromadb.PersistentClient(path="./chroma_db")
collection = chromadb_client.get_or_create_collection(name="my_collection")
embedding_model = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001", api_key=GOOGLE_API_KEY)
 
def create_and_store_embeddings(chunks):
    # chunks is a list of dicts: [{"text": str, "pdf_name": str, "page_no": int, "paragraph_no": int}, ...]
    for i, chunk in enumerate(chunks):
        text = chunk["text"]
        metadata = {
            "pdf_name": chunk["pdf_name"],
            "page_no": chunk["page_no"],
            "paragraph_no": chunk["paragraph_no"]
        }
        embeddings = embedding_model.embed_documents([text])
        collection.add(ids=[str(i)], embeddings=embeddings, documents=[text], metadatas=[metadata])   