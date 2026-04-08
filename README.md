---
title: CareerNav-Env
emoji: 🎯
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
tags:
  - openenv
---

# CareerNav-Env

A real-time OpenEnv-compliant reinforcement learning environment where an AI acts as a career coach for CS students in India.

## Environment Overview
CareerNav-Env simulates the interaction between an AI coach and diverse student personas (Lazy, Overachiever, Switcher, Panic). The goal is to minimize skill gaps for a target job role while staying within time and budget constraints, and leveraging government schemes.

## Tasks & Expected Scores
| Task ID | Name | Difficulty | Expected Match Score | Expected Reward |
| :--- | :--- | :--- | :--- | :--- |
| `skill_gap_identifier` | Skill Gap Identifier | Easy | 0.50 | 0.35 |
| `course_recommender` | Course Recommender | Medium | 0.70 | 0.35 |
| `full_optimizer` | Full Roadmap Optimizer| Hard | 0.60 | 0.35 |
| `pm_scheme_matcher` | PM Scheme Matcher | Medium-Hard | 0.55 | 0.50 |

## Action Space
- `flag_gap`: Mark a skill as missing from the student's profile.
- `recommend_course`: Assign a course from the available catalog.
- `request_more_time`: Negotiate for a budget extension based on persona archetype.
- `check_scheme_eligibility`: Verify matching with Government of India schemes.
- `finalize_roadmap`: End the episode and calculate final scores.

## Observation Space
- `student_skills`, `target_skills`, `match_score`, `gaps_remaining`, `weeks_budget`, `hours_per_week`, `market_snapshot`, `skill_graph`, `persona`, `available_schemes`, `real_courses`.

## Setup Instructions

### Local Development
1. **Create Environment**: `py -3.12 -m venv .venv`
2. **Install Deps**: `.\.venv\Scripts\pip install -r requirements.txt fpdf`
3. **Generate Data**: `.\.venv\Scripts\python.exe generate_cvs.py`
4. **Run Server**: `uvicorn server:app --port 7860`

### Docker Deployment
1. **Build**: `docker build -t careernav-env .`
2. **Run**: `docker run -p 7860:7860 careernav-env`

## Baseline Results (v1.0.0)
The environment currently employs a hardcoded baseline that flags all discovered gaps and recommends the top-ranked courses. 
Evaluation run completed on 2026-04-08 using the `overachiever` persona.
