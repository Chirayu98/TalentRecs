import numpy as np
from embedding_utils import get_embedding


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity scaled to [0,1]."""
    norm_a, norm_b = np.linalg.norm(a), np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    raw_score = float(np.dot(a, b) / (norm_a * norm_b))
    return (raw_score + 1) / 2


def generate_explanation(job_description: str, bio: str) -> str:
    """Simple placeholder explanation."""
    return f"Candidate bio compared with job description."


def rank_candidates_for_job(job_description: str, candidates: list, top_n: int = 10):
    """Rank candidates for a job by embedding similarity."""
    if not job_description:
        raise ValueError("Job description cannot be empty.")

    job_emb = get_embedding(job_description)
    scored_candidates = []

    for cand in candidates:
        bio = cand.get("bio", "")
        if not bio.strip():
            continue

        cand_emb = get_embedding(bio)
        score = cosine_sim(job_emb, cand_emb)

        explanation = generate_explanation(job_description, bio)

        scored_candidates.append({
            "candidate": cand,
            "score": round(score, 3),
            "explanation": explanation
        })

    scored_candidates.sort(key=lambda x: x["score"], reverse=True)
    return scored_candidates[:top_n]
