import requests
import json

TASKS = [
    "skill_gap_identifier",
    "course_recommender",
    "full_optimizer",
    "pm_scheme_matcher"
]

def run_task(task_id):
    server_url = "http://127.0.0.1:7860"
    session_id = f"session_{task_id}"
    
    # 1. Reset
    res = requests.post(f"{server_url}/reset", json={
        "session_id": session_id,
        "task_id": task_id,
        "cv_path": "overachiever.pdf",
        "seed": 42
    }).json()
    
    obs = res
    total_reward = 0.0
    
    # 2. Strategy: Flag all gaps
    for gap in obs.get("gaps_remaining", [])[:]:
        step_res = requests.post(f"{server_url}/step", json={
            "session_id": session_id,
            "action": {
                "action_type": "flag_gap",
                "payload": {"skill": gap}
            }
        }).json()
        total_reward += step_res["reward"]["value"]
        obs = step_res["observation"]

    # 3. Strategy: Recommend first course if gaps exist
    if obs.get("gaps_remaining") and obs.get("real_courses"):
        course_id = next(iter(obs["real_courses"]))
        step_res = requests.post(f"{server_url}/step", json={
            "session_id": session_id,
            "action": {
                "action_type": "recommend_course",
                "payload": {"course_id": course_id}
            }
        }).json()
        total_reward += step_res["reward"]["value"]
        obs = step_res["observation"]

    # 4. Strategy: Check scheme if it's the matcher task
    if task_id == "pm_scheme_matcher" and obs.get("available_schemes"):
        scheme_id = obs["available_schemes"][0]["id"]
        step_res = requests.post(f"{server_url}/step", json={
            "session_id": session_id,
            "action": {
                "action_type": "check_scheme_eligibility",
                "payload": {"scheme_id": scheme_id}
            }
        }).json()
        total_reward += step_res["reward"]["value"]
        obs = step_res["observation"]

    # 5. Finalize
    final_res = requests.post(f"{server_url}/step", json={
        "session_id": session_id,
        "action": {
            "action_type": "finalize_roadmap",
            "payload": {}
        }
    }).json()
    total_reward += final_res["reward"]["value"]
    
    return {
        "task_id": task_id,
        "match_score": final_res["observation"]["match_score"],
        "total_reward": round(total_reward, 2)
    }

def main():
    results = []
    print("Starting Baseline Evaluation...")
    for task in TASKS:
        try:
            print(f"Executing {task}...")
            res = run_task(task)
            results.append(res)
        except Exception as e:
            print(f"Error running task {task}: {e}")
            results.append({"task_id": task, "match_score": 0, "total_reward": 0, "error": str(e)})

    print("\n" + "="*60)
    print(f"{'Task ID':<30} | {'Match Score':<12} | {'Total Reward':<12}")
    print("-" * 60)
    for r in results:
        print(f"{r['task_id']:<30} | {r.get('match_score', 0.0):<12.2f} | {r.get('total_reward', 0.0):<12.2f}")
    print("="*60)

if __name__ == "__main__":
    main()
