from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains.retrieval  import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.retrievers.ensemble import EnsembleRetriever
from langchain_classic.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever 
from langchain_cohere import CohereRerank
import vectorstore_handler
from dotenv import load_dotenv
import os

import vectorstore_handler

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

def retrieve_answer(query: str, session_id: str):

    session_data = vectorstore_handler.user_sessions.get(session_id, {})
    vectorstore = session_data.get("vectorstore")
    
    if not vectorstore:
        raise ValueError("No context found! Please upload a document first.")

    semantic_retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 10}
    )

    session_docs = session_data.get("documents", [])

    if not session_docs:
        ensemble_retriever = semantic_retriever
    else:    
        bm25_retriever = BM25Retriever.from_documents(documents=session_docs, k=10)
        ensemble_retriever = EnsembleRetriever(retrievers=[bm25_retriever, semantic_retriever], weights=[0.3, 0.7])
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GOOGLE_API_KEY
    )
    compressor = CohereRerank(
        cohere_api_key=COHERE_API_KEY,
        model="rerank-english-v3.0",
        top_n=3
    )
    retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=ensemble_retriever
    )
    system_prompt = (
        "Use the provided context to answer the question. "
        "If the answer is not present in the context, say you don't know. "
        "Keep the answer concise.\n\n"
        "Context: {context}"
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}")
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, prompt)

    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    result = rag_chain.invoke({"input": query})

    return result