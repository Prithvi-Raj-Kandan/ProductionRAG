from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

embedding_model = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key=GOOGLE_API_KEY
)

persist_directory = "./chroma_db"
collection_name = "my_collection"

vectorstore = Chroma(
    collection_name=collection_name,
    embedding_function=embedding_model,
    persist_directory=persist_directory
)


def create_and_store_embeddings(chunks):

    documents = []

    for chunk in chunks:
        documents.append(
            Document(
                id = 1,
                page_content=chunk["text"],
                metadata={
                    "pdf_name": chunk["pdf_name"],
                    "page_no": chunk["page_no"],
                    "paragraph_no": chunk["paragraph_no"]
                }
            )
        )

    vectorstore.add_documents(documents)
    vectorstore.persist()