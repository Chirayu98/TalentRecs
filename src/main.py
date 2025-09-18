from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import pandas as pd
import numpy as np
import re
from typing import List, Optional
import io
from fastapi.middleware.cors import CORSMiddleware

# ----------------------------
# FastAPI app
# ----------------------------
app = FastAPI()

# ----------------------------
# CORS setup
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],  # allow both
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
candidates = None
candidate_embeddings = None

# ----------------------------
# Data Models
# ----------------------------
class JobPost(BaseModel):
    title: str
    description: str
    budget_type: str
    budget_value: float
    preferred_locations: List[str]
    remote_allowed: bool = False
    preferred_gender: Optional[str] = None

# ----------------------------
# Helpers
# ----------------------------
def get_embedding(text: str):
    """Dummy embedding: converts text into a simple numeric vector"""
    tokens = re.findall(r"\w+", str(text).lower())
    vec = np.zeros(300)
    for t in tokens:
        vec[hash(t) % 300] += 1
    return vec / (np.linalg.norm(vec) + 1e-8)

def cosine_sim(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)

def normalize_score(score):
    return (score + 1) / 2  # map -1..1 → 0..1

def extract_skills(text):
    """Safe skill extractor: handles NaN/None/float gracefully"""
    if not isinstance(text, str):
        text = "" if text is None or pd.isna(text) else str(text)
    return [s.strip().lower() for s in re.split(r"[,;/]", text) if s.strip()]

def detect_job_type(title, description):
    """Basic heuristic: management vs creative"""
    mgmt_keywords = ["manager", "lead", "director", "head", "supervisor"]
    text = f"{title} {description}".lower()
    return "management" if any(k in text for k in mgmt_keywords) else "creative"

def compute_embeddings():
    global candidate_embeddings
    if candidates is None:
        return
    embeddings = []
    for _, cand in candidates.iterrows():
        text = f"{cand.get('First Name','')} {cand.get('Last Name','')} {cand.get('Skills','')} {cand.get('Profile Description','')}"
        embeddings.append(get_embedding(text))
    candidate_embeddings = embeddings

# ----------------------------
# API Endpoints
# ----------------------------
@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    global candidates
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))

    # ✅ Replace NaN with empty strings to avoid crashes
    df = df.replace({np.nan: ""})

    candidates = df
    compute_embeddings()
    return {"status": "success", "rows": len(df)}

@app.post("/recommend")
def recommend(job: JobPost, top_k: int = 10):
    if candidates is None:
        return {"status": "error", "message": "No candidate dataset loaded."}

    compute_embeddings()

    # Job embedding
    job_text = f"{job.title}. {job.description}. Budget {job.budget_value} {job.budget_type}. Locations: {', '.join(job.preferred_locations)}"
    job_emb = get_embedding(job_text.lower())

    # Job requirements
    required_skills = extract_skills(job.description)
    job_locations_lower = [loc.lower() for loc in job.preferred_locations]
    max_views = max([cand.get("# of Views by Creators", 0) or 0 for _, cand in candidates.iterrows()]) or 1

    # Detect job type
    job_type = detect_job_type(job.title, job.description)

    # Weights
    weights = {
        "sim": 0.40 if job_type == "management" else 0.30,
        "skills": 0.25,
        "budget": 0.05 if job_type == "management" else 0.15,
        "location": 0.10,
        "popularity": 0.05 if job_type == "management" else 0.10,
        "gender": 0.15 if job_type == "management" else 0.10,
    }

    scored_candidates = []

    for idx, cand in candidates.iterrows():
        # Similarity
        sim_score = normalize_score(cosine_sim(job_emb, candidate_embeddings[idx]))

        # Skills
        cand_skills = extract_skills(cand.get("Skills", ""))
        skill_match_score = min(1.0, len(set(cand_skills) & set(required_skills)) / (len(required_skills) or 1))

        # Budget
        budget_score = 0.5
        monthly_rate, hourly_rate = cand.get("Monthly Rate"), cand.get("Hourly Rate")
        try:
            if job.budget_type == "monthly" and monthly_rate:
                rate = float(monthly_rate)
                budget_score = 1.0 if rate <= job.budget_value else max(
                    0, 1 - (rate - job.budget_value) / (job.budget_value + 1)
                )
            elif job.budget_type == "hourly" and hourly_rate:
                rate = float(hourly_rate)
                budget_score = 1.0 if rate <= job.budget_value else max(
                    0, 1 - (rate - job.budget_value) / (job.budget_value + 1)
                )
        except:
            pass

        # Location
        cand_country = str(cand.get("Country", "")).lower()
        location_score = 1.0 if cand_country in job_locations_lower else (0.7 if job.remote_allowed else 0.5)

        # Gender (strict)
        cand_gender = str(cand.get("Gender", "")).lower()
        if job.preferred_gender:
            if cand_gender == job.preferred_gender.lower():
                gender_score = 1.0
            else:
                gender_score = 0.0
        else:
            gender_score = 1.0

        # Popularity
        views = cand.get("# of Views by Creators", 0) or 0
        popularity_score = views / max_views

        # Final score
        final_score = (
            weights["sim"] * sim_score +
            weights["skills"] * skill_match_score +
            weights["budget"] * budget_score +
            weights["location"] * location_score +
            weights["popularity"] * popularity_score +
            weights["gender"] * gender_score
        )

        scored_candidates.append({
            "name": f"{cand.get('First Name','')} {cand.get('Last Name','')}".strip(),
            "gender": cand.get("Gender",""),
            "location": f"{cand.get('City','')}, {cand.get('Country','')}".strip(", "),
            "job_types": cand.get("Job Types",""),
            "skills": cand.get("Skills",""),
            "software": cand.get("Software",""),
            "platforms": cand.get("Platforms",""),
            "content_verticals": cand.get("Content Verticals",""),
            "past_creators": cand.get("Past Creators",""),
            "monthly_rate": monthly_rate,
            "hourly_rate": hourly_rate,
            "bio": cand.get("Profile Description",""),
            "views": views,
            "score": round(final_score, 3)
        })

    # Sort and return
    top_candidates = sorted(scored_candidates, key=lambda x: x["score"], reverse=True)[:top_k]
    return {"job_title": job.title, "candidates": top_candidates}
