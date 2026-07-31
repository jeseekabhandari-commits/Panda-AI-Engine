import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

load_dotenv()

def get_db_connection():
    """Establishes a secure connection to the PostgreSQL database."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

def insert_job_description(title, company, raw_text, keywords):
    """Inserts a job description into the database using parameterized queries to prevent SQL issues."""
    query = """
    INSERT INTO job_descriptions (title, company, raw_text, extracted_keywords)
    VALUES (%s, %s, %s, %s) RETURNING id;
    """
    
    conn = None
    job_id = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Safe parameterized execution
        cursor.execute(query, (title, company, raw_text, keywords))
        
        # Fetch the automatically generated UUID
        job_id = cursor.fetchone()[0]
        
        conn.commit()
        print(f"✅ Job successfully inserted! Generated ID: {job_id}")
        
        cursor.close()
    except Exception as error:
        print(f"❌ Failed to insert job: {error}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            
    return job_id


# ==========================================
# 🔍 NEW: Search & Query Functionality
# ==========================================

def search_jobs(
    search_term: Optional[str] = None, 
    keywords: Optional[List[str]] = None, 
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Queries jobs by title/company (text search) or extracted_keywords array overlap (&&).
    Uses RealDictCursor to return formatted dictionary results.
    """
    base_query = """
        SELECT id, title, company, raw_text, extracted_keywords, created_at 
        FROM job_descriptions 
        WHERE 1=1
    """
    params = []

    # Text pattern matching across Title or Company
    if search_term and search_term.strip():
        base_query += " AND (title ILIKE %s OR company ILIKE %s)"
        like_pattern = f"%{search_term.strip()}%"
        params.extend([like_pattern, like_pattern])

    # PostgreSQL Array Overlap Operator (&&) for extracted_keywords
    if keywords:
        clean_keywords = [k.strip() for k in keywords if k.strip()]
        if clean_keywords:
            base_query += " AND extracted_keywords && %s"
            params.append(clean_keywords)

    base_query += " ORDER BY created_at DESC LIMIT %s;"
    params.append(limit)

    conn = None
    results = []
    try:
        conn = get_db_connection()
        # RealDictCursor formats SQL rows directly into Python dicts
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(base_query, tuple(params))
            results = cursor.fetchall()
    except Exception as error:
        print(f"❌ Failed to execute search query: {error}")
    finally:
        if conn:
            conn.close()

    return results


if __name__ == "__main__":
    print("🧪 Test 1: Search by Skill Keyword")
    python_jobs = search_jobs(keywords=["python"])
    print(f"Found {len(python_jobs)} jobs matching 'python':")
    for j in python_jobs:
        print(f"  - [{j['company']}] {j['title']} | Keywords: {j['extracted_keywords']}")

    print("\n🧪 Test 2: Search by Text Pattern")
    ms_jobs = search_jobs(search_term="microsoft")
    print(f"Found {len(ms_jobs)} jobs matching 'microsoft':")
    for j in ms_jobs:
        print(f"  - [{j['company']}] {j['title']}")