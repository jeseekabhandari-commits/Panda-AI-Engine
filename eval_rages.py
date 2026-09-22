import os
# WORKAROUND: Mock the missing module path so Ragas doesn't crash on import
import sys
import types

try:
    import langchain_community.chat_models.vertexai
except ModuleNotFoundError:
    m = types.ModuleType("langchain_community.chat_models.vertexai")
    m.ChatVertexAI = None
    sys.modules["langchain_community.chat_models.vertexai"] = m

# Now safe to import Ragas
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# Initialize evaluator judge
evaluator_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=os.getenv("GEMINI_API_KEY")
)

evaluator_embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# Test dataset
eval_data = {
    "question": [
        "What technologies does Alex Chen specialize in?",
        "What is the capital of Nepal?"
    ],
    "contexts": [
        ["Alex Chen is a Backend & AI Engineer specialized in building REST APIs using FastAPI, PostgreSQL, and OpenAI models."],
        ["Kathmandu is the capital city of Nepal, situated in the Kathmandu Valley."]
    ],
    "answer": [
        "Alex Chen specializes in backend and AI engineering, using FastAPI, PostgreSQL, and OpenAI models.",
        "The capital of Nepal is Kathmandu, which has a population of over 1.5 million people."
    ]
}

dataset = Dataset.from_dict(eval_data)

if __name__ == "__main__":
    print("📊 Running Ragas Evaluation...")
    results = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy],
        llm=evaluator_llm,
        embeddings=evaluator_embeddings
    )
    
    df = results.to_pandas()
    print("\n================ EVALUATION RESULTS ================")
    print(df[["question", "faithfulness", "answer_relevancy"]])
    print("====================================================")