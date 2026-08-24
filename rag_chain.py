import os
from typing import List, Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from vector_store import query_vector_store
from vector_store import query_vector_store_with_scores
from reranker import filter_and_rerank_chunks
from langchain_core.chat_history import InMemoryChatMessageHistory, BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI
from vector_store import query_vector_store_with_scores
from reranker import filter_and_rerank_chunks
from sqlalchemy import create_engine
from langchain_postgres import PostgresChatMessageHistory
# Initialize Gemini Chat Model via LangChain

# Database Connection URL (e.g., PostgreSQL local or cloud URI)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/panda_db")

# Initialize SQLAlchemy Engine
engine = create_engine(DATABASE_URL)

# Table name where chat histories will be automatically created & stored
TABLE_NAME = "chat_message_history"

def get_postgres_session_history(session_id: str) -> PostgresChatMessageHistory:
    """
    Retrieves or creates a persistent PostgreSQL-backed chat history instance
    isolated by unique session_id.
    """
    return PostgresChatMessageHistory(
        table_name=TABLE_NAME,
        session_id=session_id,
        sync_connection=engine
    )

# Prompt Scaffolding
CONVERSATIONAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are an expert AI Assistant. Answer strictly based on the provided document context below.\n\nContext:\n{context}\n\nIf context is empty, state: 'I cannot find relevant information in the provided document.'"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{query}")
])

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
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

# Global session store mapping session_id -> BaseChatMessageHistory
session_store: Dict[str, BaseChatMessageHistory] = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Retrieves or creates a session chat history instance."""
    if session_id not in session_store:
        session_store[session_id] = InMemoryChatMessageHistory()
    return session_store[session_id]

# Conversational System Prompt with History Placeholder
CONVERSATIONAL_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are an expert AI Assistant. Answer questions strictly based on the provided document context below.\n\nDocument Context:\n{context}\n\nIf the context is empty or irrelevant, state: 'I cannot find relevant information in the provided document.'"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{query}")
])

llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0.2)

# Chain wrapping prompt and LLM
base_chain = CONVERSATIONAL_PROMPT | llm

# Runnable equipped with automatic history management
conversational_rag_chain = RunnableWithMessageHistory(
    base_chain,
    get_session_history,
    input_messages_key="query",
    history_messages_key="history"
)

def run_conversational_rag(tenant_id: str, session_id: str, query: str) -> Dict[str, Any]:
    """Runs multi-stage retrieval + persists dialogue state to PostgreSQL."""
    raw_results = query_vector_store_with_scores(tenant_id=tenant_id, query_text=query, top_k=8)
    filtered_chunks = filter_and_rerank_chunks(raw_results, query=query, max_distance_threshold=0.50, top_n=3)
    
    formatted_context = "\n\n---\n\n".join(filtered_chunks) if filtered_chunks else "No relevant context found."
    
    # Composite session identifier ensures multi-tenant thread isolation in Postgres
    composite_session_key = f"{tenant_id}:{session_id}"
    config = {"configurable": {"session_id": composite_session_key}}
    
    response = conversational_rag_chain.invoke(
        {"context": formatted_context, "query": query},
        config=config
    )
    
    return {
        "tenant_id": tenant_id,
        "session_id": session_id,
        "answer": response.content,
        "source_chunks": filtered_chunks
    }

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