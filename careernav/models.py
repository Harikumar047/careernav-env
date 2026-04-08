from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class StudentPersona(BaseModel):
    id: str
    archetype: str # lazy, overachiever, switcher, panic
    weeks_budget: int
    hours_per_week: int
    current_skills: List[str]

class JobData(BaseModel):
    title: str
    required_skills: List[str]
    trending_skills: Dict[str, float] = Field(default_factory=dict)

class CourseData(BaseModel):
    id: str
    title: str
    skills_covered: List[str]
    duration_hours: int
    cost: float
    url: str

class SchemeData(BaseModel):
    id: str
    name: str
    eligibility_rules: Dict[str, Any]
    stipend_amount: Optional[float] = None
    description: str

class Observation(BaseModel):
    student_skills: List[str]
    target_skills: List[str]
    match_score: float
    gaps_remaining: List[str]
    weeks_budget: int
    hours_per_week: int
    market_snapshot: Dict[str, Any]
    skill_graph: Dict[str, List[str]]
    persona: str
    available_schemes: List[Dict[str, Any]]
    real_courses: Dict[str, Dict[str, Any]]
    identified_gaps: List[str] = Field(default_factory=list)

class Action(BaseModel):
    action_type: str # flag_gap, recommend_course, finalize_roadmap, request_more_time, check_scheme_eligibility
    payload: Dict[str, Any]

class Reward(BaseModel):
    value: float
    breakdown: Dict[str, float]

class StepInfo(BaseModel):
    error: Optional[str] = None
    market_drifted: bool = False
    persona_response: Optional[str] = None
    bias_detected: bool = False
    prereq_violations: List[str] = Field(default_factory=list)
