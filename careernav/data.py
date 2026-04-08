from typing import Dict, List

# Adjacency Map: Key is the Skill, Value is the List of prerequisites required
SKILL_GRAPH: Dict[str, List[str]] = {
    "Git": [],
    "HTML": [],
    "CSS": ["HTML"],
    "JavaScript": ["HTML", "CSS"],
    "TypeScript": ["JavaScript"],
    "React": ["JavaScript"],
    "Next.js": ["React", "TypeScript"],
    "Python": [],
    "SQL": [],
    "FastAPI": ["Python"],
    "Django": ["Python"],
    "PostgreSQL": ["SQL"],
    "Redis": ["SQL"],
    "Linux": [],
    "Docker": ["Linux"],
    "Kubernetes": ["Docker"],
    "AWS": ["Linux"],
    "System Design": ["Docker", "AWS"],
    "Machine Learning": ["Python", "SQL"],
    "Deep Learning": ["Machine Learning"]
}

PERSONAS: Dict[str, Dict[str, int]] = {
    "lazy": {"weeks_budget": 12, "hours_per_week": 10},
    "overachiever": {"weeks_budget": 24, "hours_per_week": 40},
    "switcher": {"weeks_budget": 52, "hours_per_week": 20},
    "panic": {"weeks_budget": 4, "hours_per_week": 60}
}
