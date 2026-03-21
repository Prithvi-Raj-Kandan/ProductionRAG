# ProductionRAG

ProductionRAG is a Retrieval-Augmented Generation (RAG) system for querying uploaded documents through a web chat interface. It combines semantic search, keyword retrieval, reranking, and grounded answer generation with source citations.

## Key Capabilities

- Upload one or more PDF files from the frontend.
- Extract text and split into chunks for retrieval.
- Generate and store embeddings in a persistent Chroma vector database.
- Answer user questions using hybrid retrieval + reranking.
- Return answer along with source metadata (PDF, page, paragraph).
- Run evaluation with RAGAS metrics and export results to CSV.

## Technology Stack

### Backend

- Python
- FastAPI (API server)
- CORS middleware (cross-origin frontend access)
- pypdf (PDF parsing)
- LangChain ecosystem:
	- `langchain`
	- `langchain-text-splitters`
	- `langchain_chroma`
	- `langchain_google_genai`
	- `langchain_cohere`
	- `langchain_community` (BM25 retriever)
	- `langchain_classic` retrieval chains/retrievers
- ChromaDB (vector store persistence)
- Google Gemini:
	- `gemini-embedding-001` for embeddings
	- `gemini-2.5-flash` for generation/evaluation LLM
- Cohere Rerank (`rerank-english-v3.0`)
- python-dotenv (environment variable management)
- RAGAS + pandas (evaluation and reporting)

### Frontend

- React 18 + TypeScript
- Vite
- Tailwind CSS v4
- Radix UI primitives
- MUI (Material UI) packages
- Lucide icons
- Fetch API for backend communication

## Project Structure

- `main.py`: FastAPI app with upload and query endpoints.
- `pdf_handler.py`: PDF page extraction, text extraction, chunking.
- `vectorstore_handler.py`: embedding creation, Chroma persistence, document cache.
- `rag_chain.py`: retrieval pipeline, reranking, answer generation.
- `eval.py`: testset generation and RAGAS evaluation.
- `frontend_v2/`: React frontend application.
- `Uploaded_pdfs/`: uploaded input documents.
- `chroma_db/`: persisted vector database.
- `documents.json`: serialized document cache for BM25/hybrid retrieval.

## End-to-End Project Flow

1. User uploads files from the frontend (`POST /upload_pdf`).
2. Backend saves files to `Uploaded_pdfs/`.
3. PDF pages are parsed and text is extracted.
4. Text is chunked (`chunk_size=800`, `chunk_overlap=120`).
5. Each chunk is converted into embeddings and stored in ChromaDB.
6. Chunks + metadata are also written to `documents.json` for BM25 retrieval.
7. User asks a question from frontend (`GET /query?question=...`).
8. Backend retrieves candidate chunks using:
	 - semantic retriever (Chroma)
	 - BM25 retriever (when cached docs exist)
	 - weighted ensemble of both
9. Cohere reranker compresses context to top relevant chunks.
10. Gemini generates a grounded answer from retrieved context.
11. Response returns answer + source metadata.

## API Endpoints

### `POST /upload_pdf`

Uploads and processes one or more documents.

- Input: multipart form-data with `files`
- Output: success message + uploaded file list

### `GET /query`

Queries the processed document corpus.

- Input: query parameter `question`
- Output:
	- `answer`: generated response
	- `sources`: list of `{ pdf, page, paragraph }`

## Setup and Run

### 1) Backend

Prerequisites:

- Python 3.10+
- API keys for Google and Cohere

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in project root:

```env
GOOGLE_API_KEY=your_google_api_key
COHERE_API_KEY=your_cohere_api_key
```

Start backend:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2) Frontend

```bash
cd frontend_v2
npm install
npm run dev
```

Frontend default dev URL: `http://localhost:5173`

## Evaluation

Run evaluation pipeline:

```bash
python eval.py
```

Output file:

- `Evaluation_results/evaluation_results.csv`

## Notes

- Backend CORS is configured for `http://localhost:3000` and `http://localhost:5173`.
- Embeddings are added in batches with wait intervals to handle provider rate limits.
- If no relevant context exists, the response policy is to return an explicit unknown-style answer.