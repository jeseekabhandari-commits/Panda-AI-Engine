import os
import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any

# 1. Initialize Local ChromaDB Vector Store with Persistence
vector_db_path = "./chroma_db_store"
chroma_client = chromadb.PersistentClient(path=vector_db_path)

# Use standard sentence transformer or Gemini embedding model
embedding_fn = embedding_functions.DefaultEmbeddingFunction()

collection = chroma_client.get_or_create_collection(
    name="pandy_rag_knowledge",
    embedding_function=embedding_fn,
    metadata={"hnsw:space": "cosine"}  # Metric for semantic distance
)

# 2. Recursive Chunking Function with Overlap
def recursive_text_chunker(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """Splits long documents into overlapping semantic chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

# 3. Vector Ingestion Pipeline with Multi-Tenant Metadata
def ingest_document(doc_id: str, tenant_id: str, raw_text: str):
    chunks = recursive_text_chunker(raw_text)
    
    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"tenant_id": tenant_id, "doc_id": doc_id, "chunk_index": i} for i in range(len(chunks))]
    
    collection.add(
        documents=chunks,
        metadatas=metadatas,
        ids=ids
    )
    return {"status": "success", "chunks_stored": len(chunks)}

# 4. Semantic Similarity Query
def query_vector_store(tenant_id: str, query_text: str, top_k: int = 3) -> Dict[str, Any]:
    results = collection.query(
        query_texts=[query_text],
        n_results=top_k,
        where={"tenant_id": tenant_id}  # Enforces B2B Tenant Isolation
    )
    return results["documents"][0] if results["documents"] else []

def query_vector_store_with_scores(tenant_id: str, query_text: str, top_k: int = 10) -> list[dict]:
    """
    Queries ChromaDB and returns documents alongside their cosine distance scores.
    Lower distance = Higher semantic similarity.
    """
    results = collection.query(
        query_texts=[query_text],
        n_results=top_k,
        where={"tenant_id": tenant_id},
        include=["documents", "distances"]
    )
    
    if not results or "documents" not in results or not results["documents"][0]:
        return []

    docs = results["documents"][0]
    distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)

    return [{"content": doc, "distance": dist} for doc, dist in zip(docs, distances)]