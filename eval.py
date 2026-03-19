"""from ragas import evaluate
from ragas.metrics.collections import faithfulness , answer_correctness
from ragas.testset import TestsetGenerator
import vectorstore_handler
from ragas.llms import LangchainLLMWrapper
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
load_dotenv()

EVAL_DIR = "Evaluation_results"
os.makedirs(EVAL_DIR, exist_ok=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def evaluate_pipeline():
    generator_llm = LangchainLLMWrapper(ChatGoogleGenerativeAI(google_api_key=GOOGLE_API_KEY, model="gemini-2.5-flash"))
    generator = TestsetGenerator(llm=generator_llm, embedding_model=vectorstore_handler.embedding_model)
    dataset = generator.generate_with_langchain_docs(vectorstore_handler.documents, testset_size=20)
    score = evaluate(dataset, metrics=[faithfulness, answer_correctness])
    df = score.to_pandas()
    file_path = os.path.join(EVAL_DIR, "evaluation_results.csv")
    df.to_csv(file_path, index=False)  # to_csv writes directly to path, returns None
    print(f"Evaluation results saved to {file_path}")
    return df

evaluate_pipeline()
"""