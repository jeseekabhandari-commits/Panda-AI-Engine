from typing import List, Dict, Any

def filter_and_rerank_chunks(
    raw_results: List[Dict[str, Any]], 
    query: str, 
    max_distance_threshold: float = 0.50, 
    top_n: int = 3
) -> List[str]:
    """
    1. Distance Thresholding: Filters out chunks with distance > max_distance_threshold.
    2. Candidate Re-ranking: Re-scores remaining candidates based on query term frequency overlap.
    3. Truncates to top_n highest-precision chunks.
    """
    # 1. Similarity Distance Thresholding
    valid_candidates = [
        item for item in raw_results if item["distance"] <= max_distance_threshold
    ]
    
    if not valid_candidates:
        return []

    # 2. Heuristic Re-ranking (Term Overlap Score Boost)
    query_terms = set(query.lower().split())
    
    for candidate in valid_candidates:
        content_words = candidate["content"].lower().split()
        overlap_count = sum(1 for word in query_terms if word in content_words)
        
        # Combined Score: Inverse distance boosted by term match ratio
        term_match_ratio = overlap_count / max(len(query_terms), 1)
        candidate["rerank_score"] = (1.0 - candidate["distance"]) + (0.2 * term_match_ratio)

    # Sort descending by re-rank score
    valid_candidates.sort(key=lambda x: x["rerank_score"], reverse=True)

    # 3. Return top_n text contents
    return [c["content"] for c in valid_candidates[:top_n]]