import os
import sys
import types
from dataclasses import dataclass
from typing import Dict, Any, List

# 1. Inject runtime module mock for deprecated VertexAI import path
try:
    import langchain_community.chat_models.vertexai
except ModuleNotFoundError:
    m = types.ModuleType("langchain_community.chat_models.vertexai")
    m.ChatVertexAI = type("ChatVertexAI", (object,), {})
    sys.modules["langchain_community.chat_models.vertexai"] = m

import docx
from datasets import Dataset
from ragas import evaluate
from ragas.metrics.collections import faithfulness, answer_relevancy
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

FAITHFULNESS_PASS = 0.80
FAITHFULNESS_CRITICAL = 0.60
ANSWER_RELEVANCY_PASS = 0.75

@dataclass
class GuardrailResult:
    status: str
    action: str
    faithfulness_score: float
    relevancy_score: float
    output_text: str

class ProductionRAGEngine:
    def __init__(self, doc_path: str):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
        
        self.doc_path = doc_path
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            temperature=0, 
            google_api_key=self.api_key
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004", 
            google_api_key=self.api_key
        )
        self.raw_text = self._extract_docx_text()

    def _extract_docx_text(self) -> str:
        doc = docx.Document(self.doc_path)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

    def _retrieve_chunks(self, chunk_size: int = 500, top_k: int = 3) -> List[str]:
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=50)
        chunks = splitter.split_text(self.raw_text)
        return chunks[:top_k] if len(chunks) >= top_k else chunks

    def generate_response(self, query: str, contexts: List[str], strict_mode: bool = False) -> str:
        if strict_mode:
            prompt = (
                f"Strict Mode Active.\nContext:\n{contexts}\n\n"
                f"Question: {query}\n"
                f"Provide a short answer using ONLY facts directly mentioned above."
            )
        else:
            prompt = f"Context:\n{contexts}\n\nQuestion: {query}\nAnswer directly from context:"
        
        response = self.llm.invoke(prompt)
        return response.content

    def evaluate_generation(self, query: str, contexts: List[str], answer: str) -> Dict[str, float]:
        dataset = Dataset.from_dict({
            "question": [query],
            "contexts": [[c for c in contexts]],
            "answer": [answer]
        })
        
        results = evaluate(
            dataset=dataset,
            metrics=[faithfulness, answer_relevancy],
            llm=self.llm,
            embeddings=self.embeddings,
            show_progress=False
        )
        
        df = results.to_pandas()
        return {
            "faithfulness": float(df["faithfulness"].iloc[0]),
            "relevancy": float(df["answer_relevancy"].iloc[0])
        }

    def execute_pipeline(self, user_query: str) -> GuardrailResult:
        contexts = self._retrieve_chunks(chunk_size=500, top_k=2)
        initial_answer = self.generate_response(user_query, contexts, strict_mode=False)
        
        scores = self.evaluate_generation(user_query, contexts, initial_answer)
        faith_score = scores["faithfulness"]
        rel_score = scores["relevancy"]

        if faith_score >= FAITHFULNESS_PASS and rel_score >= ANSWER_RELEVANCY_PASS:
            return GuardrailResult(
                status="APPROVED",
                action="DIRECT_SERVE",
                faithfulness_score=faith_score,
                relevancy_score=rel_score,
                output_text=initial_answer
            )

        if faith_score < FAITHFULNESS_CRITICAL:
            return GuardrailResult(
                status="FLAGGED",
                action="HUMAN_REVIEW_QUEUE",
                faithfulness_score=faith_score,
                relevancy_score=rel_score,
                output_text="[System Notice] Output held for manual validation due to low grounding confidence."
            )

        expanded_contexts = self._retrieve_chunks(chunk_size=750, top_k=4)
        retry_answer = self.generate_response(user_query, expanded_contexts, strict_mode=True)
        retry_scores = self.evaluate_generation(user_query, expanded_contexts, retry_answer)

        if retry_scores["faithfulness"] >= FAITHFULNESS_PASS:
            return GuardrailResult(
                status="RECOVERED",
                action="FALLBACK_SERVE",
                faithfulness_score=retry_scores["faithfulness"],
                relevancy_score=retry_scores["relevancy"],
                output_text=retry_answer
            )
        else:
            return GuardrailResult(
                status="FLAGGED",
                action="HUMAN_REVIEW_QUEUE",
                faithfulness_score=retry_scores["faithfulness"],
                relevancy_score=retry_scores["relevancy"],
                output_text="[System Notice] Output held for manual validation following failed retry."
            )

if __name__ == "__main__":
    engine = ProductionRAGEngine("sample.docx")
    query = "What are the key details and metrics outlined in the document?"
    
    result = engine.execute_pipeline(query)
    print("\n================ PIPELINE RESULT ================")
    print(f"Status:             {result.status}")
    print(f"Action Taken:       {result.action}")
    print(f"Faithfulness Score: {result.faithfulness_score:.2f}")
    print(f"Relevancy Score:    {result.relevancy_score:.2f}")
    print(f"Output Text:\n{result.output_text}")
    print("=================================================")