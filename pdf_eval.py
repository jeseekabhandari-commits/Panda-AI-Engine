import os
import sys
import types
import pytest
import fitz  # PyMuPDF
from datasets import Dataset

# 1. Silence legacy import paths on startup with a proper dummy class
import sys
import types

try:
    import langchain_community.chat_models.vertexai
except ModuleNotFoundError:
    m = types.ModuleType("langchain_community.chat_models.vertexai")
    m.ChatVertexAI = type("ChatVertexAI", (object,), {})
    sys.modules["langchain_community.chat_models.vertexai"] = m

from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 2. Define Strict CI/CD Quality Thresholds
FAITHFULNESS_THRESHOLD = 0.80
ANSWER_RELEVANCY_THRESHOLD = 0.75

def extract_pdf_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = "".join([page.get_text() for page in doc])
    return text

def build_eval_dataset(pdf_path: str, user_query: str, llm):
    raw_text = extract_pdf_text(pdf_path)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_text(raw_text)
    
    retrieved_contexts = chunks[:2] if len(chunks) >= 2 else chunks
    prompt = f"Context:\n{retrieved_contexts}\n\nQuestion: {user_query}\nAnswer directly from context:"
    response = llm.invoke(prompt)
    
    return Dataset.from_dict({
        "question": [user_query],
        "contexts": [retrieved_contexts],
        "answer": [response.content]
    })

# 3. Pytest Integration Entrypoint
@pytest.mark.ragas_ci
def test_pdf_rag_quality():
    api_key = os.getenv("GEMINI_API_KEY")
    assert api_key, "❌ CI/CD Error: GEMINI_API_KEY environment variable is not set."

    pdf_file = "sample.pdf"
    assert os.path.exists(pdf_file), f"❌ CI/CD Error: Missing test artifact '{pdf_file}'."

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, google_api_key=api_key)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004", google_api_key=api_key)
    query = "What are the key technical specifications and features detailed in the document?"

    dataset = build_eval_dataset(pdf_file, query, llm)
    
    # Execute Ragas Evaluation
    results = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy],
        llm=llm,
        embeddings=embeddings
    )
    
    df = results.to_pandas()
    faith_score = float(df["faithfulness"].iloc[0])
    relevancy_score = float(df["answer_relevancy"].iloc[0])

    print(f"\n--- EVALUATION SCORES ---")
    print(f"Faithfulness: {faith_score:.2f} (Threshold: {FAITHFULNESS_THRESHOLD})")
    print(f"Answer Relevancy: {relevancy_score:.2f} (Threshold: {ANSWER_RELEVANCY_THRESHOLD})")

    # 4. CI/CD Assertions
    assert faith_score >= FAITHFULNESS_THRESHOLD, (
        f"❌ Pipeline Failed: Faithfulness score {faith_score:.2f} is below threshold {FAITHFULNESS_THRESHOLD}. "
        "The response contains ungrounded context claims or hallucinations."
    )
    
    assert relevancy_score >= ANSWER_RELEVANCY_THRESHOLD, (
        f"❌ Pipeline Failed: Answer Relevancy score {relevancy_score:.2f} is below threshold {ANSWER_RELEVANCY_THRESHOLD}. "
        "The generated answer did not sufficiently address the query."
    )