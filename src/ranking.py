import numpy as np
from embedding_utils import get_embedding
from llm_utils import generate_explanation


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors safely.
    Returns a value in [0, 1] (normalized).
    """
    norm_a, norm_b = np.linalg.norm(a), np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    raw_score = float(np.dot(a, b) / (norm_a * norm_b))
    return (raw_score + 1) / 2  # scale from [-1, 1] → [0, 1]


def rank_candidates_for_job(job_description: str, candidates: list, top_n: int = 10):
    """
    Rank candidates for a given job description using embeddings and cosine similarity.
    
    Args:
        job_description (str): Job title/description text.
        candidates (list): List of candidate dicts (must contain 'bio').
        top_n (int): Number of top candidates to return.

    Returns:
        list of dict: Each dict contains candidate info, score, and LLM explanation.
    """
    if not job_description:
        raise ValueError("Job description cannot be empty.")

    job_emb = get_embedding(job_description)
    scored_candidates = []

    for cand in candidates:
        bio = cand.get("bio", "")
        if not bio.strip():
            continue  # skip if no bio

        cand_emb = get_embedding(bio)
        score = cosine_sim(job_emb, cand_emb)

        explanation = generate_explanation(job_description, bio)

        scored_candidates.append({
            "candidate": cand,
            "score": round(score, 3),
            "explanation": explanation
        })

    # Sort by score (descending) and return top_n
    scored_candidates.sort(key=lambda x: x["score"], reverse=True)
    return scored_candidates[:top_n]
