import math
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from rank_bm25 import BM25Okapi

# PostgreSQL connection configurations
DB_PARAMS = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "postgres",
    "host": "127.0.0.1",
    "port": "5433"
}

def get_all_tenant_chunks(tenant_id: str) -> List[str]:
    """Retrieves all raw text chunks belonging to a specific tenant from pgvector."""
    query = "SELECT content FROM panda_document_chunks WHERE tenant_id = %s;"
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute(query, (tenant_id,))
                rows = cur.fetchall()
                return [row[0] for row in rows]
    except Exception as e:
        print(f"[Error] Fetching tenant chunks from Postgres failed: {e}")
        return []

def query_vector_store_with_scores(tenant_id: str, query_embedding: List[float], top_k: int = 8) -> List[Dict[str, Any]]:
    """Performs native vector similarity search in pgvector using cosine distance (<=>)."""
    query = """
        SELECT content, 1 - (embedding <=> %s::vector) AS similarity
        FROM panda_document_chunks
        WHERE tenant_id = %s
        ORDER BY embedding <=> %s::vector ASC
        LIMIT %s;
    """
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (query_embedding, tenant_id, query_embedding, top_k))
                results = cur.fetchall()
                return [dict(row) for row in results]
    except Exception as e:
        print(f"[Error] pgvector query failed: {e}")
        return []

def bm25_search(corpus_chunks: List[str], query: str, top_k: int = 8) -> List[Dict[str, Any]]:
    """Runs BM25 tokenized keyword search over the full tenant document corpus."""
    if not corpus_chunks or not query.strip():
        return []

    tokenized_corpus = [doc.lower().split() for doc in corpus_chunks if doc.strip()]
    if not tokenized_corpus:
        return []

    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)
    
    scored_chunks = [
        {"content": chunk, "bm25_score": float(score)}
        for chunk, score in zip(corpus_chunks, scores) if score > 0.0
    ]
    
    scored_chunks.sort(key=lambda x: x["bm25_score"], reverse=True)
    return scored_chunks[:top_k]

def reciprocal_rank_fusion(
    dense_results: List[Dict[str, Any]], 
    sparse_results: List[Dict[str, Any]], 
    k: int = 60
) -> List[Dict[str, Any]]:
    """Combines dense and sparse ranked result lists using Reciprocal Rank Fusion (RRF)."""
    rrf_scores: Dict[str, float] = {}
    doc_map: Dict[str, Dict[str, Any]] = {}

    for rank, item in enumerate(dense_results):
        doc_content = item["content"]
        doc_map[doc_content] = item
        rrf_scores[doc_content] = rrf_scores.get(doc_content, 0.0) + (1.0 / (k + rank + 1))

    for rank, item in enumerate(sparse_results):
        doc_content = item["content"]
        if doc_content not in doc_map:
            doc_map[doc_content] = item
        rrf_scores[doc_content] = rrf_scores.get(doc_content, 0.0) + (1.0 / (k + rank + 1))

    sorted_docs = sorted(rrf_scores.keys(), key=lambda doc: rrf_scores[doc], reverse=True)
    return [doc_map[doc] for doc in sorted_docs]

def hybrid_retrieve(tenant_id: str, query: str, query_embedding: List[float], top_k: int = 8) -> List[Dict[str, Any]]:
    """Performs hybrid dense (pgvector) + sparse (BM25) retrieval fused via RRF."""
    # 1. Fetch Dense Candidates from PostgreSQL
    dense_candidates = query_vector_store_with_scores(
        tenant_id=tenant_id, 
        query_embedding=query_embedding, 
        top_k=top_k
    )
    
    # 2. Fetch ALL Tenant Documents from PostgreSQL for Sparse BM25 Search
    all_tenant_chunks = get_all_tenant_chunks(tenant_id)
    sparse_candidates = bm25_search(corpus_chunks=all_tenant_chunks, query=query, top_k=top_k)
    
    # 3. Perform Reciprocal Rank Fusion
    fused_results = reciprocal_rank_fusion(dense_candidates, sparse_candidates, k=60)
    return fused_results

if __name__ == "__main__":
    print("Testing Hybrid Retriever against PostgreSQL...")
    # Dummy testing call
    dummy_embedding = [0.0] * 768  # Adjust dimension based on your Gemini embedding length
    results = hybrid_retrieve(
        tenant_id="test_tenant", 
        query="test search query", 
        query_embedding=dummy_embedding
    )
    print(f"Retrieved {len(results)} results.")

def init_db():
    """Initializes the pgvector extension and document table if they do not exist."""
    init_commands = [
        "CREATE EXTENSION IF NOT EXISTS vector;",
        """
        CREATE TABLE IF NOT EXISTS panda_document_chunks (
            id SERIAL PRIMARY KEY,
            tenant_id VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            embedding vector(768)
        );
        """
    ]
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                for cmd in init_commands:
                    cur.execute(cmd)
            conn.commit()
        print("Database initialized successfully with pgvector extension.")
    except Exception as e:
        print(f"[Error] Database initialization failed: {e}")

if __name__ == "__main__":
    print("Testing Hybrid Retriever against PostgreSQL...")
    
    # 1. Ensure table and pgvector extension exist
    init_db()
    
    # 2. Test hybrid retrieval
    dummy_embedding = [0.0] * 768  # Adjust vector dimension if needed
    results = hybrid_retrieve(
        tenant_id="test_tenant", 
        query="test search query", 
        query_embedding=dummy_embedding
    )
    print(f"Retrieved {len(results)} results.")

