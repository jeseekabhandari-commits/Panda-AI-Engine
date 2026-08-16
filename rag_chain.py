import os
from typing import List, Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from vector_store import query_vector_store

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

def run_rag_pipeline(tenant_id: str, query: str, top_k: int = 4) -> Dict[str, Any]:
    """
    1. Retrieves top-k matching chunks for tenant_id from ChromaDB.
    2. Formats context into LangChain prompt template.
    3. Invokes Gemini LLM to produce grounded answer.
    """
    # 1. Retrieve vector chunks
    retrieved_chunks = query_vector_store(tenant_id=tenant_id, query_text=query, top_k=top_k)
    
    if not retrieved_chunks:
        return {
            "answer": "No relevant documents found for this tenant.",
            "source_chunks": []
        }
        
    # 2. Combine chunk texts into single context block
    formatted_context = "\n\n---\n\n".join(retrieved_chunks)
    
    # 3. Format prompt and invoke LLM
    formatted_prompt = prompt_template.format(context=formatted_context, query=query)
    response = llm.invoke(formatted_prompt)
    
    return {
        "answer": response.content,
        "source_chunks": retrieved_chunks
    }