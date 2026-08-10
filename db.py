import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import List, Optional, Dict, Any

# Fetch connection string from environment variables
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/panda_db")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# --- 1. INSERT INITIAL BATCH JOB ---
def create_batch_job(batch_id: str, job_id: str, total_files: int):
    query = """
    INSERT INTO batch_jobs (batch_id, job_id, status, total_files, processed_files, created_at)
    VALUES (%s, %s, 'PENDING', %s, 0, NOW());
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (batch_id, job_id, total_files))
        conn.commit()

# --- 2. UPDATE PROGRESS & SAVE MATCH RESULT ---
def save_candidate_result_and_update_progress(
    batch_id: str, 
    filename: str, 
    jaccard_score: float, 
    match_percentage: float, 
    matched_skills: List[str], 
    missing_skills: List[str]
):
    insert_result_query = """
    INSERT INTO match_results (batch_id, filename, jaccard_score, match_percentage, matched_skills, missing_skills)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    
    update_batch_query = """
    UPDATE batch_jobs 
    SET processed_files = processed_files + 1,
        status = CASE 
            WHEN processed_files + 1 >= total_files THEN 'COMPLETED' 
            ELSE 'PROCESSING' 
        END,
        completed_at = CASE 
            WHEN processed_files + 1 >= total_files THEN NOW() 
            ELSE NULL 
        END
    WHERE batch_id = %s;
    """
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Save candidate match output
            cur.execute(insert_result_query, (
                batch_id, filename, jaccard_score, match_percentage, matched_skills, missing_skills
            ))
            # Increment processed_files and update status automatically
            cur.execute(update_batch_query, (batch_id,))
        conn.commit()

# --- 3. RETRIEVE BATCH JOB PROGRESS ---
def get_batch_job_from_db(batch_id: str) -> Optional[Dict[str, Any]]:
    query = "SELECT * FROM batch_jobs WHERE batch_id = %s;"
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (batch_id,))
            return cur.fetchone()

# --- 4. RETRIEVE RANKED MATCH RESULTS ---
def get_match_results_by_batch(batch_id: str) -> List[Dict[str, Any]]:
    query = """
    SELECT filename, jaccard_score, match_percentage, matched_skills, missing_skills
    FROM match_results 
    WHERE batch_id = %s
    ORDER BY jaccard_score DESC;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (batch_id,))
            return cur.fetchall()