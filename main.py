from fastapi import FastAPI, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os 
from typing import List
from pdf_handler import extract_pages_from_pdf, create_chunks, extract_text_from_pages
from vectorstore_handler import create_and_store_embeddings 
import logging
from rag_chain import retrieve_answer

logging.basicConfig(level=logging.INFO)
app = FastAPI()
logger = logging.getLogger(__name__)

# allow frontend origin for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "Uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload_pdf")
async def upload_pdf(files: List[UploadFile]):
    uploaded_files = []
    try:   
        for file in files:
            file_location = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_location, "wb") as buffer:
                buffer.write(file.file.read())
            uploaded_files.append(file.filename)    
        logger.info(f"Uploaded files: {uploaded_files}")
    except Exception as e: 
        logger.error(f"Error uploading files: {e}")
        return {"error": "Failed to upload files."}
    
    # Process all uploaded PDFs
    try:
        pdf_paths = [os.path.join(UPLOAD_DIR, f) for f in uploaded_files]
        pages = extract_pages_from_pdf(pdf_paths)
        logger.info(f"Extracted {len(pages)} pages from PDFs.")
    except Exception as e:
        logger.error(f"Error processing PDFs: {e}")
        return {"error": "Failed to process PDFs."}
    
    try:
        all_text = extract_text_from_pages(pages)
    except Exception as e:
        logger.error(f"Error extracting text from pages: {e}")
        return {"error": "Failed to extract text from pages."}
    
    try:
        chunk_texts = create_chunks(all_text)  # Returns list of strings
        # Build chunks with metadata using page info
        chunks_with_metadata = []
        chunk_index = 0
        for page in pages:
            # Split chunks per page (approximate; adjust if needed)
            page_chunks = chunk_texts[chunk_index:chunk_index + len(chunk_texts) // len(pages) + 1]  # Simple distribution
            for i, chunk_text in enumerate(page_chunks):
                chunks_with_metadata.append({
                    "text": chunk_text,
                    "pdf_name": page["pdf_name"],
                    "page_no": page["page_no"],
                    "paragraph_no": i + 1  # Sequential per page
                })
            chunk_index += len(page_chunks)
    except Exception as e:
        logger.error(f"Error creating chunks: {e}")
        return {"error": "Failed to create chunks from text."}   
    
    # Store embeddings in vector store
    try:
        create_and_store_embeddings(chunks_with_metadata)
        logger.info(f"Stored {len(chunks_with_metadata)} chunks in ChromaDB.")
    except Exception as e:
        logger.error(f"Error creating/storing embeddings: {e}")
        return {"error": "Failed to create/store embeddings."}
        
    return {"message": f"Files uploaded and processed successfully at {UPLOAD_DIR}", "files": uploaded_files}
import os

@app.get("/query")
def query(question: str):
    try:
        result = retrieve_answer(question)

        sources = []

        for doc in result["context"]:
            sources.append({
                "pdf": os.path.basename(doc.metadata.get("pdf_name", "")),
                "page": doc.metadata.get("page_no"),
                "paragraph": doc.metadata.get("paragraph_no")
            })

        return {
            "answer": result["answer"],
            "sources": sources
        }

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return {"error": "Failed to process query."}