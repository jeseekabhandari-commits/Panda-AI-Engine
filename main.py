from fastapi import FastAPI, HTTPException, status, File, UploadFile, Form
from pydantic import BaseModel, Field
from typing import List, Dict, Any

from extractor import ResumeExtractor
from pdf_parser import extract_text_from_pdf_bytes
# Import your matcher and DB services from previous days
# from matcher import ResumeMatcher
# from ingest_service import get_job_skills_from_db

app = FastAPI(
    title="AI Resume Matching Engine",
    description="API for extracting resume skills via Gemini and matching against PostgreSQL job listings.",
    version="1.0.0"
)

# Initialize models and extractors once on startup
extractor = ResumeExtractor()


# --- Pydantic Schemas for Request/Response Validation ---

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


# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"status": "online", "message": "Panda-AI-Engine API is up and running!"}

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Simple health check endpoint to verify API server status."""
    return {"status": "online", "engine": "Gemini + PostgreSQL Matcher"}


@app.post("/api/v1/match-resume", response_model=MatchResponse, status_code=status.HTTP_200_OK)
def match_resume_to_job(payload: ResumeMatchRequest):
    """
    Accepts raw resume text and job_id, extracts candidate skills using Gemini,
    retrieves required skills from PostgreSQL, and computes match metrics.
    """
    try:
        # 1. Extract candidate skills using Gemini pipeline
        extraction_result = extractor.extract_resume_skills(payload.resume_text)
        candidate_skills = set(extraction_result.get("candidate_skills", []))

        # 2. Mock/Fetch required skills from database (replace with your DB call)
        # required_skills = set(get_job_skills_from_db(payload.job_id))
        required_skills = {"Python", "PostgreSQL", "FastAPI", "Docker", "Git"}  # Example DB result

        if not required_skills:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job ID '{payload.job_id}' not found in database."
            )

        # 3. Calculate Jaccard Similarity and Skill Gaps
        intersection = candidate_skills.intersection(required_skills)
        union = candidate_skills.union(required_skills)

        jaccard_score = round(len(intersection) / len(union), 4) if union else 0.0
        match_percentage = round(jaccard_score * 100, 2)

        matched_skills = list(intersection)
        missing_skills = list(required_skills - candidate_skills)

        # 4. Return structured response payload
        return MatchResponse(
            job_id=payload.job_id,
            jaccard_score=jaccard_score,
            match_percentage=match_percentage,
            extracted_skills=list(candidate_skills),
            matched_skills=matched_skills,
            missing_skills=missing_skills
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline processing error: {str(e)}"
        )

@app.post("/api/v1/match-resume-file", status_code=status.HTTP_200_OK)
async def match_resume_file_to_job(
    file: UploadFile = File(..., description="PDF Resume file to parse"),
    job_id: str = Form(..., description="Target Job ID stored in database")
):
    """Accepts a PDF resume file upload, extracts text, and matches candidate skills."""
    # 1. Validate file extension
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF files (.pdf) are supported."
        )

    # 2. Read binary stream
    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded PDF file is empty."
        )

    # 3. Extract text using our pdf_parser module
    extracted_resume_text = extract_text_from_pdf_bytes(file_bytes)

    # 4. Extract skills via Gemini
    extraction_result = extractor.extract_resume_skills(extracted_resume_text)
    candidate_skills = set(extraction_result.get("candidate_skills", []))

    # 5. Target skills (Database lookup simulation)
    required_skills = {"Python", "PostgreSQL", "FastAPI", "Docker", "Git"}

    # 6. Calculate set operations
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