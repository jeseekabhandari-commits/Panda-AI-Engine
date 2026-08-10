import logging
import time
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any

from fastapi import (
    FastAPI, BackgroundTasks, HTTPException, status, 
    File, UploadFile, Form, Request
)
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from google.api_core.exceptions import GoogleAPIError, ServiceUnavailable

from extractor import ResumeExtractor
from pdf_parser import extract_text_from_pdf_bytes
from db import (
    create_batch_job, 
    save_candidate_result_and_update_progress, 
    get_batch_job_from_db, 
    get_match_results_by_batch
)

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("uvicorn.error")

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI App
app = FastAPI(title="Panda AI Engine")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize Extractor
extractor = ResumeExtractor()


# --- Pydantic Schemas ---

class BatchStatusEnum(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ResumeMatchRequest(BaseModel):
    resume_text: str = Field(..., min_length=10, description="Raw text extracted from candidate resume")
    job_id: str = Field(..., description="Target Job ID stored in PostgreSQL")

class MatchResponse(BaseModel):
    job_id: str
    jaccard_score: float
    match_percentage: float
    extracted_skills: List[str]
    matched_skills: List[str]
    missing_skills: List[str]

class CandidateMatchResult(BaseModel):
    filename: str
    jaccard_score: float
    match_percentage: float
    matched_skills: List[str]
    missing_skills: List[str]

class BatchResultsResponse(BaseModel):
    batch_id: str
    job_id: str
    total_candidates: int
    results: List[CandidateMatchResult]


# --- Helper Utility Functions ---

def extract_skills_with_retry(text: str, max_retries: int = 3) -> dict:
    """Calls Gemini API with exponential backoff retry logic for transient errors."""
    retries = 0
    delay = 2

    while retries < max_retries:
        try:
            # Execute extraction via ResumeExtractor
            extraction_result = extractor.extract_resume_skills(text)
            extracted = extraction_result.get("candidate_skills", [])
            required = ["Python", "PostgreSQL", "FastAPI", "Docker", "Git"]  # Standard target baseline
            return {
                "extracted_skills": extracted,
                "required_skills": required
            }
        except (ServiceUnavailable, GoogleAPIError, ConnectionResetError, OSError) as e:
            retries += 1
            logger.warning(f"⚠️ Gemini API attempt {retries}/{max_retries} failed: {str(e)}. Retrying in {delay}s...")
            if retries >= max_retries:
                logger.error(f"Gemini API unreachable after {max_retries} attempts.")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="AI extraction service is temporarily overloaded. Please try again later."
                )
            time.sleep(delay)
            delay *= 2


def process_single_resume_worker(batch_id: str, filename: str, file_bytes: bytes, job_id: str):
    """Background worker processing single PDF parsing and database execution."""
    try:
        text = extract_text_from_pdf_bytes(file_bytes)
        data = extract_skills_with_retry(text)
        
        extracted = data["extracted_skills"]
        required = data["required_skills"]
        
        matched = list(set(extracted) & set(required))
        missing = list(set(required) - set(extracted))
        
        union_set = set(extracted + required)
        jaccard = len(matched) / len(union_set) if union_set else 0.0
        match_percentage = round(jaccard * 100, 2)
        
        save_candidate_result_and_update_progress(
            batch_id=batch_id,
            filename=filename,
            jaccard_score=jaccard,
            match_percentage=match_percentage,
            matched_skills=matched,
            missing_skills=missing
        )
    except HTTPException as http_ex:
        logger.error(f"HTTP Exception for {filename}: {http_ex.detail}")
    except Exception as e:
        logger.error(f"Unexpected error processing {filename}: {str(e)}")


# --- Endpoints ---

@app.get("/")
def read_root():
    return FileResponse("templates/index.html")

@app.get("/dashboard")
async def get_dashboard():
    return FileResponse("templates/index.html")

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "online", "engine": "Gemini + PostgreSQL Matcher"}

@app.post("/api/v1/match-resume", response_model=MatchResponse, status_code=status.HTTP_200_OK)
def match_resume_to_job(payload: ResumeMatchRequest):
    try:
        extraction_result = extractor.extract_resume_skills(payload.resume_text)
        candidate_skills = set(extraction_result.get("candidate_skills", []))
        required_skills = {"Python", "PostgreSQL", "FastAPI", "Docker", "Git"}

        intersection = candidate_skills.intersection(required_skills)
        union = candidate_skills.union(required_skills)

        jaccard_score = round(len(intersection) / len(union), 4) if union else 0.0
        match_percentage = round(jaccard_score * 100, 2)

        return MatchResponse(
            job_id=payload.job_id,
            jaccard_score=jaccard_score,
            match_percentage=match_percentage,
            extracted_skills=list(candidate_skills),
            matched_skills=list(intersection),
            missing_skills=list(required_skills - candidate_skills)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline processing error: {str(e)}"
        )

@app.post("/api/v1/match-resume-file", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def match_resume_file_to_job(
    request: Request,
    file: UploadFile = File(..., description="PDF Resume file to parse"),
    job_id: str = Form(..., description="Target Job ID stored in database")
):
    logger.info(f"Received resume upload: {file.filename} for Job ID: {job_id}")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF files (.pdf) are supported."
        )

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded PDF file is empty."
        )

    extracted_resume_text = extract_text_from_pdf_bytes(file_bytes)
    data = extract_skills_with_retry(extracted_resume_text)
    
    candidate_skills = set(data["extracted_skills"])
    required_skills = set(data["required_skills"])

    intersection = candidate_skills.intersection(required_skills)
    union = candidate_skills.union(required_skills)
    jaccard_score = round(len(intersection) / len(union), 4) if union else 0.0

    return {
        "filename": file.filename,
        "job_id": job_id,
        "jaccard_score": jaccard_score,
        "match_percentage": round(jaccard_score * 100, 2),
        "extracted_skills": list(candidate_skills),
        "matched_skills": list(intersection),
        "missing_skills": list(required_skills - candidate_skills)
    }

@app.post("/api/v1/match-resumes-batch", status_code=status.HTTP_202_ACCEPTED)
async def match_resumes_batch(
    background_tasks: BackgroundTasks,
    job_id: str = Form(...),
    files: List[UploadFile] = File(...)
):
    batch_id = str(uuid.uuid4())
    total_files = len(files)
    
    create_batch_job(batch_id=batch_id, job_id=job_id, total_files=total_files)
    
    for file in files:
        contents = await file.read()
        background_tasks.add_task(
            process_single_resume_worker,
            batch_id=batch_id,
            filename=file.filename,
            file_bytes=contents,
            job_id=job_id
        )
        
    return {
        "batch_id": batch_id,
        "message": f"Enqueued {total_files} resume(s) for background processing.",
        "status_url": f"/api/v1/batch-status/{batch_id}"
    }

@app.get("/api/v1/batch-status/{batch_id}")
def get_batch_status(batch_id: str):
    job = get_batch_job_from_db(batch_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Batch ID '{batch_id}' not found."
        )
    return job

@app.get("/api/v1/batch-results/{batch_id}", response_model=BatchResultsResponse)
def get_batch_results(batch_id: str):
    job = get_batch_job_from_db(batch_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Batch ID '{batch_id}' not found."
        )
        
    if job["status"] != BatchStatusEnum.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Batch is currently '{job['status']}'. Wait until status is COMPLETED."
        )
        
    results = get_match_results_by_batch(batch_id)
    return {
        "batch_id": batch_id,
        "job_id": job["job_id"],
        "total_candidates": len(results),
        "results": results
    }