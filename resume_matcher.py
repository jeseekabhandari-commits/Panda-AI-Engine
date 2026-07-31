from typing import List, Dict, Any, Set

class ResumeMatcher:
    """
    Core matching engine to evaluate resume skill coverage against job requirements.
    """
    def __init__(self, resume_text: str, candidate_skills: List[str]):
        self.resume_text = resume_text
        self.candidate_skills = set([s.strip().lower() for s in candidate_skills if s.strip()])

    def calculate_jaccard_similarity(self, job_skills: List[str]) -> float:
        """
        Calculates Jaccard similarity score between candidate skills and job requirements.
        Score range: 0.0 to 1.0 (0% to 100% match).
        """
        target_skills = set([s.strip().lower() for s in job_skills if s.strip()])
        
        if not target_skills and not self.candidate_skills:
            return 1.0
        if not target_skills or not self.candidate_skills:
            return 0.0

        intersection = self.candidate_skills.intersection(target_skills)
        union = self.candidate_skills.union(target_skills)

        return round(len(intersection) / len(union), 4)

    def analyze_skill_gap(self, job_skills: List[str]) -> Dict[str, Any]:
        """
        Identifies matched skills, missing required skills, and overall match percentage.
        """
        target_skills = set([s.strip().lower() for s in job_skills if s.strip()])
        
        matched_skills = list(self.candidate_skills.intersection(target_skills))
        missing_skills = list(target_skills.difference(self.candidate_skills))
        extra_skills = list(self.candidate_skills.difference(target_skills))

        # Direct percentage match based on target skills coverage
        coverage_score = 0.0
        if target_skills:
            coverage_score = round(len(matched_skills) / len(target_skills) * 100, 2)

        jaccard_score = self.calculate_jaccard_similarity(job_skills)

        return {
            "match_percentage": coverage_score,
            "jaccard_similarity": round(jaccard_score * 100, 2),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "extra_skills": extra_skills
        }