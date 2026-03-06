from typing import List
from langchain_google_genai import GoogleGenerativeAI 
from langchain_classic.chains import retrieval_qa
from langchain_community.vectorstores import Chroma
import os
from dotenv import load_dotenv
from vectorstore_handler import chromadb_client, collection, embedding_model

load_dotenv()  
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def retrieve_answer(query: str):
    vectorstore = Chroma(client=chromadb_client, collection=collection, embedding_function=embedding_model) 
    retriever = vectorstore.as_retriever(search_type='similarity' , search_kwargs={"k": 3})
    llm = GoogleGenerativeAI(model="gemini-2.0-flash", api_key=GOOGLE_API_KEY)
    qa_chain = retrieval_qa(llm=llm, retriever=retriever, return_source_documents=True)
    result = qa_chain.invoke({"query": query})
    answer = result["result"]
    return answer
