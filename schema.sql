-- Enable UUID extension for secure, non-sequential primary keys
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Job Descriptions Registry
CREATE TABLE IF NOT EXISTS job_descriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    raw_text TEXT NOT NULL,
    extracted_keywords TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Resumes Registry
CREATE TABLE IF NOT EXISTS resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_name VARCHAR(255),
    email VARCHAR(255),
    raw_text TEXT NOT NULL,
    skills TEXT[],
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Evaluation Scores Matrix
CREATE TABLE IF NOT EXISTS analysis_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES job_descriptions(id) ON DELETE CASCADE,
    resume_id UUID REFERENCES resumes(id) ON DELETE CASCADE,
    match_score INT CHECK (match_score >= 0 AND match_score <= 100),
    keyword_matrix JSONB,
    gap_analysis TEXT,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for quantitative ranking queries (Must target sub-50ms read criteria)
CREATE INDEX IF NOT EXISTS idx_scores_match ON analysis_scores(match_score DESC);

-- Track batch lifecycle
CREATE TABLE IF NOT EXISTS batch_jobs (
    batch_id VARCHAR(36) PRIMARY KEY,
    job_id VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    total_files INT NOT NULL,
    processed_files INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Track individual resume evaluation results within a batch
CREATE TABLE IF NOT EXISTS match_results (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(36) REFERENCES batch_jobs(batch_id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    jaccard_score FLOAT NOT NULL,
    match_percentage FLOAT NOT NULL,
    matched_skills TEXT[] NOT NULL,
    missing_skills TEXT[] NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);