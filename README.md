# ProductionRAG

ProductionRAG is a document QA system built with Retrieval-Augmented Generation (RAG). It lets users upload PDFs and ask questions through a web chat interface, returning grounded answers with source references.

## Tech Stack

- Backend: Python, FastAPI, LangChain, ChromaDB, Google Gemini, Cohere Rerank
- Frontend: React + TypeScript (Vite), Tailwind CSS, Radix UI
- Evaluation: RAGAS, pandas

## Project Structure

- `backend/main.py`: FastAPI app and request handling
- `backend/pdf_handler.py`: PDF parsing and chunking
- `backend/vectorstore_handler.py`: embeddings and vector store persistence
- `backend/rag_chain.py`: retrieval, reranking, and answer generation
- `backend/eval.py`: evaluation pipeline
- `frontend_v2/`: frontend client
- `Uploaded_pdfs/`: uploaded files

## Quick Start

### Backend

Requirements:

- Python 3.10+
- Google and Cohere API keys

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` in the project root:

```env
GOOGLE_API_KEY=your_google_api_key
COHERE_API_KEY=your_cohere_api_key
```

Run backend:

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend_v2
npm install
npm run dev
```

Frontend runs by default at `http://localhost:5173`.

## Evaluation

```bash
cd backend
python eval.py
```

Results are saved to `Evaluation_results/evaluation_results.csv`.

## Notes

- Backend CORS allows localhost frontend development origins.
- If retrieval has insufficient context, the assistant returns an unknown-style response.