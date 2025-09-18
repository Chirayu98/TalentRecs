from transformers import pipeline

# Load the model once (FLAN-T5 is a good balance between size and quality)
llm = pipeline("text2text-generation", model="google/flan-t5-base")

def generate_explanation(job, candidate, scores):
    """
    Generate a natural-language explanation why a candidate is a good/weak fit.
    """
    prompt = f"""
    Job: {job.description}
    Candidate: {candidate.get('name')}
    Skills: {candidate.get('skills')}
    Location: {candidate.get('location')}
    Gender: {candidate.get('gender')}
    Popularity: {candidate.get('popularity')}

    Matching Scores:
    - Embedding similarity: {scores.get('similarity')}
    - Skill overlap: {scores.get('skill_overlap')}
    - Budget match: {scores.get('budget')}
    - Location match: {scores.get('location')}
    - Gender match: {scores.get('gender')}
    - Popularity weight: {scores.get('popularity')}

    Please explain in simple recruiter-friendly language why this candidate is a good or weak fit.
    """

    response = llm(prompt, max_length=200, clean_up_tokenization_spaces=True)
    return response[0]['generated_text']
