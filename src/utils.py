import pandas as pd

def load_candidates(filepath: str):
    """
    Load candidate data from Excel file and return as list of dicts.
    """
    candidates = pd.read_excel(filepath).to_dict(orient="records")
    return candidates

def load_jobs():
    """
    Example function to load or define jobs dictionary.
    You can extend to load from file if needed.
    """
    jobs = {
        "job1": "Looking for a web developer with React and backend experience",
        "job2": "Data scientist with machine learning and Python skills",
    }
    return jobs
