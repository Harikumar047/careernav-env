import json
from ..models import JobData

def fetch_job_market(target_role: str) -> JobData:
    """Mock implementation returning static snapshot for a Software Engineer."""
    # In live, this hits Adzuna / Naukri API
    return JobData(
        title=target_role,
        required_skills=["Python", "SQL", "Machine Learning", "FastAPI"],
        trending_skills={
            "Deep Learning": 0.85,
            "AWS": 0.70,
            "React": 0.65
        }
    )
