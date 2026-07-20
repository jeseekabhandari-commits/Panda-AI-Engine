# ingest_service.py
import psycopg2
import os
from dotenv import load_dotenv

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
    # Updated to match your exact database columns: title, company, extracted_keywords
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

