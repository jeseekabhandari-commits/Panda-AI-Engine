import os
import json
from typing import List, Dict, Any, AsyncGenerator

from sqlalchemy import create_engine
from langchain_postgres import PostgresChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI

from hybrid_retriever import hybrid_retrieve
from reranker import filter_and_rerank_chunks

# Database Connection URL (Targeting pgvector container)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/postgres")
engine = create_engine(DATABASE_URL)
TABLE_NAME = "chat_message_history"

def get_postgres_session_history(session_id: str) -> PostgresChatMessageHistory:
    """
    Retrieves or creates a persistent PostgreSQL-backed chat history instance
    isolated by unique composite session_id (e.g. tenant_id:session_id).
    """
    return PostgresChatMessageHistory(
        table_name=TABLE_NAME,
        session_id=session_id,
        sync_connection=engine
    )

def get_hybrid_context(tenant_id: str, query: str) -> List[str]:
    """Retrieves high-precision context using pgvector hybrid RRF and re-ranking."""
    raw_fused_results = hybrid_retrieve(tenant_id=tenant_id, query=query, top_k=8)
    filtered_chunks = filter_and_rerank_chunks(
        raw_fused_results, 
        query=query, 
        max_distance_threshold=0.50, 
        top_n=3
    )
    return filtered_chunks

def track_token_usage(response_obj: Any) -> None:
    """Day 82 Token and Cost Tracking Wrapper."""
    if hasattr(response_obj, "usage_metadata") and response_obj.usage_metadata:
        usage = response_obj.usage_metadata
        prompt_tokens = getattr(usage, "prompt_token_count", 0)
        completion_tokens = getattr(usage, "candidates_token_count", 0)
        total_tokens = getattr(usage, "total_token_count", 0)
        print(f"\n[Token Tracker] Prompt: {prompt_tokens} | Completion: {completion_tokens} | Total: {total_tokens}")

# Conversational System Prompt with History Placeholder
CONVERSATIONAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are an expert AI Assistant. Answer questions strictly based on the provided document context below.\n\nDocument Context:\n{context}\n\nIf the context is empty or irrelevant, state: 'I cannot find relevant information in the provided document.'"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{query}")
])

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash", 
    temperature=0.2,
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# Chain wrapping prompt and LLM
base_chain = CONVERSATIONAL_PROMPT | llm

# Runnable equipped with persistent PostgreSQL history management
conversational_rag_chain = RunnableWithMessageHistory(
    base_chain,
    get_postgres_session_history,  # Bound directly to PostgreSQL chat history
    input_messages_key="query",
    history_messages_key="history"
)

def run_conversational_rag(tenant_id: str, session_id: str, query: str) -> Dict[str, Any]:
    """Runs pgvector hybrid retrieval + persists dialogue state to PostgreSQL."""
    filtered_chunks = get_hybrid_context(tenant_id=tenant_id, query=query)
    formatted_context = "\n\n---\n\n".join(filtered_chunks) if filtered_chunks else "No relevant context found."
    
    # Composite session key ensures tenant-isolated chat history threads in Postgres
    composite_session_key = f"{tenant_id}:{session_id}"
    config = {"configurable": {"session_id": composite_session_key}}
    
    response = conversational_rag_chain.invoke(
        {"context": formatted_context, "query": query},
        config=config
    )
    
    # Track usage
    track_token_usage(response)
    
    return {
        "tenant_id": tenant_id,
        "session_id": session_id,
        "answer": response.content,
        "source_chunks": filtered_chunks
    }

async def stream_conversational_rag(
    tenant_id: str, 
    session_id: str, 
    query: str
) -> AsyncGenerator[str, None]:
    """Asynchronously yields SSE formatted tokens from the RAG chain."""
    filtered_chunks = get_hybrid_context(tenant_id=tenant_id, query=query)
    formatted_context = "\n\n---\n\n".join(filtered_chunks) if filtered_chunks else "No relevant context found."
    
    composite_session_key = f"{tenant_id}:{session_id}"
    config = {"configurable": {"session_id": composite_session_key}}
    
    # Send metadata event first
    metadata = {
        "event": "metadata",
        "tenant_id": tenant_id,
        "session_id": session_id,
        "source_chunks": filtered_chunks
    }
    yield f"data: {json.dumps(metadata)}\n\n"
    
    # Async stream LLM tokens
    async for chunk in conversational_rag_chain.astream(
        {"context": formatted_context, "query": query},
        config=config
    ):
        token_content = chunk.content if hasattr(chunk, "content") else str(chunk)
        if token_content:
            payload = {"event": "token", "content": token_content}
            yield f"data: {json.dumps(payload)}\n\n"

    yield f"data: {json.dumps({'event': 'done'})}\n\n"

import google.generativeai as genai

# Define the usage tracker function
def track_gemini_usage(response):
    """Tracks token consumption for Day 82 analytics."""
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        usage = response.usage_metadata
        prompt_tokens = usage.prompt_token_count
        candidate_tokens = usage.candidates_token_count
        total_tokens = usage.total_token_count
        print(f"\n[Token Tracker] Prompt: {prompt_tokens} | Completion: {candidate_tokens} | Total: {total_tokens}")
    else:
        print("\n[Token Tracker] Usage metadata unavailable.")

# Inside your main generation function:
def generate_answer(prompt: str):
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Generate content from Gemini
    response = model.generate_content(prompt)
    
    # ADD STEP 3 HERE: Track tokens immediately after response returns
    track_gemini_usage(response)
    
    return response.text