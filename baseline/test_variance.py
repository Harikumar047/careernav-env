import requests

URL = "http://localhost:7860"

def run_strategy(name, actions):
    print(f"\n--- Running {name} ---")
    session_id = f"test_{name.replace(' ', '_')}"
    
    # Reset
    res = requests.post(f"{URL}/reset", json={
        "session_id": session_id,
        "task_id": "full_optimizer",
        "cv_path": "overachiever.pdf",
        "seed": 42
    }).json()
    
    obs = res
    rewards = []
    
    for action in actions:
        if action == "auto_flag":
            gaps = obs.get("gaps_remaining", [])
            for gap in gaps:
                step_res = requests.post(f"{URL}/step", json={
                    "session_id": session_id,
                    "action": {"action_type": "flag_gap", "payload": {"skill": gap}}
                }).json()
                rewards.append(step_res["reward"]["value"])
                obs = step_res["observation"]
        elif action == "auto_recommend":
            courses = obs.get("real_courses", {})
            gaps = obs.get("gaps_remaining", [])
            course_ids = [cid for cid, c in courses.items() if any(g in c['skills_covered'] for g in gaps)][:3]
            for cid in course_ids:
                step_res = requests.post(f"{URL}/step", json={
                    "session_id": session_id,
                    "action": {"action_type": "recommend_course", "payload": {"course_id": cid}}
                }).json()
                rewards.append(step_res["reward"]["value"])
                obs = step_res["observation"]
        else:
            step_res = requests.post(f"{URL}/step", json={
                "session_id": session_id,
                "action": action
            }).json()
            rewards.append(step_res["reward"]["value"])
            obs = step_res["observation"]
            
    # Always finalize at the end just in case action list didn't include it
    if not any(isinstance(a, dict) and a.get("action_type") == "finalize_roadmap" for a in actions):
        step_res = requests.post(f"{URL}/step", json={
            "session_id": session_id,
            "action": {"action_type": "finalize_roadmap", "payload": {}}
        }).json()
        rewards.append(step_res["reward"]["value"])
        obs = step_res["observation"]
        
    score = obs.get("match_score", 0.0)
    rewards_str = ",".join([f"{r:.2f}" for r in rewards])
    print(f"[END] score={score:.3f} rewards={rewards_str}")

# Strat 1: Reset then immediately finalize
run_strategy("Strategy 1", [{"action_type": "finalize_roadmap", "payload": {}}])

# Strat 2: Reset then flag all gaps, then finalize
run_strategy("Strategy 2", ["auto_flag", {"action_type": "finalize_roadmap", "payload": {}}])

# Strat 3: Reset then recommend 3 courses, then finalize
run_strategy("Strategy 3", ["auto_recommend", {"action_type": "finalize_roadmap", "payload": {}}])
