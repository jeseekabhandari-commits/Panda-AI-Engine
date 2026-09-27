import sys
import types
import os
import json
import warnings
from datasets import Dataset
import logging
logging.getLogger("google_genai").setLevel(logging.ERROR)
# --- STEP 1: IN-MEMORY MOCK FOR BROKEN RAGAS VERTEXAI IMPORT ---
fake_vertex = types.ModuleType("langchain_community.chat_models.vertexai")
fake_vertex.ChatVertexAI = type("ChatVertexAI", (), {})
sys.modules["langchain_community.chat_models.vertexai"] = fake_vertex

# --- STEP 2: SUPPRESS NON-BREAKING WARNINGS ---
warnings.filterwarnings("ignore", category=FutureWarning)

# --- STEP 3: IMPORT RAGAS (USING answer_relevancy) ---
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# 1. Initialize Gemini Judge and Embeddings
eval_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.0,
    google_api_key=os.getenv("GEMINI_API_KEY")
)

eval_embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# 2. Evaluation Dataset
eval_data = {
    "question": [
        "What database engine is used for vector storage?",
        "How is chat history isolated in multi-tenant environments?"
    ],
    "contexts": [
        ["PostgreSQL with pgvector extension handles high-dimensional vector storage and hybrid retrieval."],
        ["Chat history is isolated using a composite session key formatted as tenant_id:session_id in PostgresChatMessageHistory."]
    ],
    "answer": [
        "The system uses PostgreSQL with the pgvector extension for storing and searching vector embeddings.",
        "Multi-tenant isolation is achieved by prefixing session IDs with the tenant ID (tenant_id:session_id)."
    ],
    "ground_truth": [
        "PostgreSQL with pgvector is used for vector storage.",
        "Session histories are isolated using a composite key consisting of tenant_id and session_id."
    ]
}

def run_evaluation():
    print("\n[Day 84] Initiating Ragas Metric Evaluation...")
    
    dataset = Dataset.from_dict(eval_data)
    
    results = evaluate(
        dataset=dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision
        ],
        llm=eval_llm,
        embeddings=eval_embeddings
    )
    
    df_results = results.to_pandas()
    print("\n=== Evaluation Telemetry Results ===")
    print(df_results)
    
    df_results.to_json("eval_telemetry_day84.json", orient="records", indent=2)
    print("\n[Day 84] Results exported to eval_telemetry_day84.json")

if __name__ == "__main__":
    run_evaluation()