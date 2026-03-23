from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os 
import shutil
from typing import List
from backend.pdf_handler import extract_pages_from_pdf, create_chunks, extract_text_from_pages
from backend.vectorstore_handler import create_and_store_embeddings, delete_session_data
import logging
from backend.rag_chain import retrieve_answer

logging.basicConfig(level=logging.INFO)
app = FastAPI()
logger = logging.getLogger(__name__)

frontend_origins = os.getenv("FRONTEND_ORIGINS", "http://localhost:3000,http://localhost:5173")
allow_origins = [origin.strip() for origin in frontend_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "Uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/upload_pdf")
async def upload_pdf(files: List[UploadFile], session_id: str = Form(...)):
    uploaded_files = []
    session_upload_dir = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(session_upload_dir, exist_ok=True)
    
    try:   
        for file in files:
            file_location = os.path.join(session_upload_dir, file.filename)
            with open(file_location, "wb") as buffer:
                buffer.write(file.file.read())
            uploaded_files.append(file.filename)    
        logger.info(f"Uploaded files: {uploaded_files}")
    except Exception as e: 
        logger.error(f"Error uploading files: {e}")
        return {"error": "Failed to upload files."}

    try:
        pdf_paths = [os.path.join(session_upload_dir, f) for f in uploaded_files]
        pages = extract_pages_from_pdf(pdf_paths)
        logger.info(f"Extracted {len(pages)} pages from PDFs.")
    except Exception as e:
        logger.error(f"Error processing PDFs: {e}")
        return {"error": "Failed to process PDFs."}
    
    try:
        all_text = extract_text_from_pages(pages)
        logger.info(f"Extracted text from {len(pages)} pages.")
    except Exception as e:
        logger.error(f"Error extracting text from pages: {e}")
        return {"error": "Failed to extract text from pages."}
    
    try:
        chunk_texts = create_chunks(all_text)  
        chunks_with_metadata = []
        chunk_index = 0
        for page in pages:
            page_chunks = chunk_texts[chunk_index:chunk_index + len(chunk_texts) // len(pages) + 1]  # Simple distribution
            for i, chunk_text in enumerate(page_chunks):
                chunks_with_metadata.append({
                    "text": chunk_text,
                    "pdf_name": page["pdf_name"],
                    "page_no": page["page_no"],
                    "paragraph_no": i + 1  
                })
            chunk_index += len(page_chunks)
        logger.info(f"Created {len(chunks_with_metadata)} chunks with metadata.")    
    except Exception as e:
        logger.error(f"Error creating chunks: {e}")
        return {"error": "Failed to create chunks from text."}   
    
    try:
        create_and_store_embeddings(chunks_with_metadata, session_id)
        logger.info(f"Stored {len(chunks_with_metadata)} chunks in ChromaDB for session {session_id}.")
    except Exception as e:
        logger.error(f"Error creating/storing embeddings: {e}")
        error_str = str(e).lower()
        if "429" in error_str or "quota" in error_str or "resource_exhausted" in error_str or "rate limit" in error_str:
            return JSONResponse(status_code=429, content={"error": "API rate limit reached. Please try again after some time."})
        return JSONResponse(status_code=500, content={"error": "Failed to create/store embeddings."})
        
    return {"message": f"Files uploaded and processed successfully", "files": uploaded_files}

@app.get("/query")
async def query(question: str, session_id: str):
    try:
        result = retrieve_answer(question, session_id)
        sources = []

        for doc in result["context"]:
            sources.append({
                "pdf": os.path.basename(doc.metadata.get("pdf_name", "")),
                "page": doc.metadata.get("page_no"),
                "paragraph": doc.metadata.get("paragraph_no")
            })
        logger.info(f"Query: {question}, Answer: {result['answer']}, Sources: {sources}")
        return {
            "answer": result["answer"],
            "sources": sources
        }

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        error_str = str(e).lower()
        if "429" in error_str or "quota" in error_str or "resource_exhausted" in error_str or "rate limit" in error_str:
            return JSONResponse(status_code=429, content={"error": "API rate limit reached. Please try again after some time."})
        return JSONResponse(status_code=500, content={"error": "Failed to process query."})

@app.delete("/cleanup")
@app.post("/cleanup")
async def cleanup(session_id: str):
    try:
        session_upload_dir = os.path.join(UPLOAD_DIR, session_id)
        if os.path.exists(session_upload_dir):
            shutil.rmtree(session_upload_dir)
        
        delete_session_data(session_id)
        logger.info(f"Cleaned up session {session_id} successfully.")
        return {"message": "Session cleaned up."}
    except Exception as e:
        logger.error(f"Error cleaning up session: {e}")
        return {"error": "Failed to cleanup."}