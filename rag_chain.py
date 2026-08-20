import os
from typing import List, Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from vector_store import query_vector_store
from vector_store import query_vector_store_with_scores
from reranker import filter_and_rerank_chunks

# Initialize Gemini Chat Model via LangChain
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.2,
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# Define Grounded RAG Prompt Template
RAG_PROMPT_TEMPLATE = """
You are an expert AI Assistant answering questions strictly based on the provided retrieved context.

Context Information:
---------------------
{context}
---------------------

Instructions:
- Answer the user query using ONLY the context provided above.
- If the answer cannot be determined from the context, state clearly: "I cannot find relevant information in the provided document."
- Do NOT make up or extrapolate facts outside the context.

User Query: {query}

Answer:
"""

prompt_template = PromptTemplate(
    input_variables=["context", "query"],
    template=RAG_PROMPT_TEMPLATE
)

def run_rag_pipeline(tenant_id: str, query: str, top_k: int = 8) -> Dict:
    raw_results = query_vector_store_with_scores(tenant_id=tenant_id, query_text=query, top_k=top_k)
    
    # 2. Apply distance thresholding and re-ranking
    filtered_chunks = filter_and_rerank_chunks(
        raw_results=raw_results, 
        query=query, 
        max_distance_threshold=0.50, 
        top_n=3
    )
    
    # Early exit if zero chunks pass distance threshold
    if not filtered_chunks:
        return {
            "answer": "I cannot find relevant information in the provided document.",
            "source_chunks": []
        }
        
    # 3. Format grounded context for Gemini
    formatted_context = "\n\n---\n\n".join(filtered_chunks)
    formatted_prompt = prompt_template.format(context=formatted_context, query=query)
    response = llm.invoke(formatted_prompt)
    
    return {
        "answer": response.content,
        "source_chunks": filtered_chunks
    }