from typing import List
from ..models import CourseData

def recommend_courses(skills: List[str]) -> List[CourseData]:
    """Mock implementation returning static course recommendations."""
    # In live, this hits Coursera and Udemy APIs
    courses = []
    if "Python" in skills or not courses:
        courses.append(CourseData(id="py101", title="Python for Everybody (Coursera)", skills_covered=["Python"], duration_hours=40, cost=0.0, url="https://coursera.org/mock-python"))
    if "Machine Learning" in skills:
        courses.append(CourseData(id="ml201", title="Machine Learning Specialization (Coursera)", skills_covered=["Machine Learning", "Python"], duration_hours=80, cost=49.0, url="https://coursera.org/mock-ml"))
    if "Docker" in skills or "Kubernetes" in skills:
        courses.append(CourseData(id="dk301", title="Docker Mastery (Udemy)", skills_covered=["Docker", "Linux"], duration_hours=15, cost=10.0, url="https://udemy.com/mock-docker"))
    if "React" in skills or "JavaScript" in skills:
        courses.append(CourseData(id="web101", title="Modern React Sandbox", skills_covered=["React", "JavaScript", "HTML"], duration_hours=30, cost=15.0, url="https://udemy.com/mock-react"))
    if "SQL" in skills:
        courses.append(CourseData(id="sql101", title="SQL Bootcamp", skills_covered=["SQL"], duration_hours=15, cost=10.0, url="https://udemy.com/mock-sql"))
    if "FastAPI" in skills:
        courses.append(CourseData(id="fa101", title="FastAPI Masterclass", skills_covered=["FastAPI", "Python"], duration_hours=10, cost=15.0, url="https://udemy.com/mock-fastapi"))
    return courses
