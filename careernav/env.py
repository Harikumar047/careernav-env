import random
from typing import Dict, Any, Tuple
from .models import Observation, Action, Reward, StepInfo
from .data import SKILL_GRAPH, PERSONAS
from .fetchers.jobs import fetch_job_market
from .fetchers.courses import recommend_courses
from .fetchers.schemes import get_available_schemes
from .fetchers.resume import parse_resume

class CareerNavEnv:
    def __init__(self):
        self._state: Observation = None
        self._step_count = 0
        self._done = False
        
        # Internal state for tracking interactions
        self._current_persona_key = None
        self._recommended_courses = []
        self._flagged_gaps = set()
        self._schemes_matched = []
        self._initial_gap_count = 0
        
    def reset(self, cv_path: str = "lazy.pdf", target_role: str = "Software Engineer", seed: int = None) -> Observation:
        if seed is not None:
            random.seed(seed)
        self._step_count = 0
        self._done = False
        self._recommended_courses = []
        self._flagged_gaps = set()
        self._schemes_matched = []
        
        # Pick persona
        for key in PERSONAS.keys():
            if key in cv_path.lower():
                self._current_persona_key = key
                break
        if not self._current_persona_key:
            self._current_persona_key = "switcher"
            
        persona_data = PERSONAS[self._current_persona_key]
        
        # Parse logic
        student_skills = parse_resume(cv_path)
        job_data = fetch_job_market(target_role)
        
        gaps = [s for s in job_data.required_skills if s not in student_skills]
        
        # Score
        match_score = len(set(student_skills).intersection(job_data.required_skills)) / len(job_data.required_skills) if job_data.required_skills else 1.0

        courses = recommend_courses(gaps)
        schemes = get_available_schemes()
        
        self._state = Observation(
            student_skills=student_skills,
            target_skills=job_data.required_skills,
            match_score=match_score,
            gaps_remaining=gaps,
            weeks_budget=persona_data["weeks_budget"],
            hours_per_week=persona_data["hours_per_week"],
            market_snapshot=job_data.trending_skills,
            skill_graph=SKILL_GRAPH,
            persona=self._current_persona_key,
            available_schemes=[s.model_dump() for s in schemes],
            real_courses={c.id: c.model_dump() for c in courses},
            identified_gaps=[]
        )
        self._initial_gap_count = len(gaps)
        return self._state

    def state(self) -> Observation:
        return self._state

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, StepInfo]:
        if self._done:
            return self._state, Reward(value=0, breakdown={"error": 0.0}), self._done, StepInfo(error="Environment is done")
        
        self._step_count += 1
        reward_val = 0.0
        breakdown = {}
        info = StepInfo()
        
        # Market Drift Simulation (Step 5)
        if self._step_count == 5:
            info.market_drifted = True
            if self._state.market_snapshot:
                top_skill = max(self._state.market_snapshot, key=self._state.market_snapshot.get)
                if top_skill not in self._state.target_skills:
                    self._state.target_skills.append(top_skill)
                    if top_skill not in self._state.student_skills:
                        self._state.gaps_remaining.append(top_skill)
                        
        action_type = action.action_type
        payload = action.payload
        
        # Bias check
        if "justification" in payload:
            justification = payload["justification"].lower()
            if any(term in justification for term in ["college", "tier", "name", "john", "jane", "bob", "alice"]):
                info.bias_detected = True
                reward_val -= 0.25
                breakdown["bias_penalty"] = -0.25

        if action_type == "flag_gap":
            skill = payload.get("skill")
            if skill in self._state.gaps_remaining and skill not in self._flagged_gaps:
                self._flagged_gaps.add(skill)
                if skill not in self._state.identified_gaps:
                    self._state.identified_gaps.append(skill)
                reward_val += 0.15
                breakdown["correct_flag"] = 0.15
                self._state.match_score = round(
                    min(1.0, self._state.match_score + 0.05), 3)
            else:
                reward_val -= 0.05
                breakdown["false_gap"] = -0.05
                
        elif action_type == "recommend_course":
            course_id = payload.get("course_id")
            course = None
            for c in self._state.real_courses.values():
                if c["id"] == course_id:
                    course = c
                    break
            
            if course:
                total_budget_hours = self._state.weeks_budget * self._state.hours_per_week
                if course["duration_hours"] > total_budget_hours:
                    reward_val -= 0.15
                    breakdown["budget_overrun"] = -0.15
                else:
                    prereq_violations = []
                    for skill in course["skills_covered"]:
                        prereqs = SKILL_GRAPH.get(skill, [])
                        for pq in prereqs:
                            if pq not in self._state.student_skills and pq not in self._flagged_gaps:
                                prereq_violations.append(pq)
                    
                    if prereq_violations:
                        reward_val -= 0.10
                        breakdown["prereq_violation"] = -0.10
                        info.prereq_violations = prereq_violations
                    else:
                        reward_val += 0.20
                        breakdown["correct_course"] = 0.20
                        
                    self._recommended_courses.append(course_id)
                    for s in course["skills_covered"]:
                        if s not in self._state.student_skills:
                            self._state.student_skills.append(s)
                        if s in self._state.gaps_remaining:
                            self._state.gaps_remaining.remove(s)
            else:
                reward_val -= 0.05
                
        elif action_type == "request_more_time":
            prob = {"lazy": 0.1, "panic": 0.8, "overachiever": 0.9, "switcher": 0.5}.get(self._state.persona, 0.5)
            if random.random() < prob:
                self._state.weeks_budget += 4
                info.persona_response = "Accepted"
            else:
                info.persona_response = "Rejected"
                
        elif action_type == "check_scheme_eligibility":
            scheme_id = payload.get("scheme_id")
            scheme = next((s for s in self._state.available_schemes 
                if s["id"] == scheme_id), None)
            if not scheme:
                reward_val -= 0.05
                info.error = "Invalid scheme_id"
            else:
                match_ok = self._state.match_score >= 0.2
                is_cs = any(s in self._state.student_skills 
                    for s in ["Python","Java","JavaScript",
                              "C++","React","SQL"])
                eligible_map = {
                    "pm_internship_01": 
                        self._state.persona in ["overachiever","switcher","panic"],
                    "sih_01": 
                        self._state.persona in ["overachiever","switcher"],
                    "aicte_01": True,
                    "csir_01": match_ok and is_cs,
                    "nasscom_01": is_cs,
                }
                is_eligible = eligible_map.get(scheme_id, False)
                if is_eligible:
                    reward_val += 0.15
                    breakdown["scheme_match"] = 0.15
                    if scheme_id not in self._schemes_matched:
                        self._schemes_matched.append(scheme_id)
                else:
                    reward_val += 0.05
                    breakdown["partial_scheme"] = 0.05
                    info.error = f"Not eligible for {scheme_id}"
                    
        elif action_type == "finalize_roadmap":
            self._done = True
            gaps_closed = self._initial_gap_count - len(
                self._state.gaps_remaining)
            coverage = gaps_closed / max(self._initial_gap_count, 1)
            scheme_bonus = 0.2 if len(self._schemes_matched) > 0 else 0.0
            reward_val = round(
                0.3 * coverage + 
                0.5 * self._state.match_score + 
                0.2 * scheme_bonus, 3)
            
            if self._step_count < 3:
                reward_val -= 0.20
                breakdown["too_early"] = -0.20
                
            breakdown["final_reward"] = reward_val
            
        # 3. match_score must be recalculated after every step
        if self._state.target_skills:
            matched = len(set(self._state.student_skills)
                .intersection(set(self._state.target_skills)))
            self._state.match_score = round(
                matched / len(self._state.target_skills), 3)
        else:
            self._state.match_score = 1.0
                
        return self._state, Reward(value=reward_val, breakdown=breakdown), self._done, info
