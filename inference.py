import os
import requests
import json
from openai import OpenAI
from typing import List, Dict, Any

# Environment & Model Config
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")
HF_TOKEN = os.getenv("HF_TOKEN")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")

SERVER_URL = os.getenv("CAREERNAV_URL", "https://harikumar07-careernav-env.hf.space")

client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)

TASKS = [
    "skill_gap_identifier",
    "course_recommender",
    "full_optimizer",
    "pm_scheme_matcher"
]

def get_agent_action(obs: Dict[str, Any], task_id: str) -> Dict[str, Any]:
    prompt = f"""
    You are an AI Career Coach in the CareerNav environment.
    Task: {task_id}
    Current Observation: {json.dumps(obs, indent=2)}
    
    Goal:
    - If skill_gap_identifier: Flag all missing skills using 'flag_gap'.
    - If course_recommender: Recommend suitable courses for gaps using 'recommend_course'.
    - If pm_scheme_matcher: Check eligibility for relevant government schemes using 'check_scheme_eligibility'.
    - If full_optimizer: Combine all actions to create the best roadmap.
    
    Respond ONLY with a JSON object matching this schema:
    {{
        "action_type": "<type>",
        "payload": {{ ... }}
    }}
    Action types: flag_gap, recommend_course, finalize_roadmap, request_more_time, check_scheme_eligibility
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        # Try to extract JSON from response
        content = response.choices[0].message.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        return json.loads(content)
    except Exception as e:
        # Fallback to finalizing if anything goes wrong
        return {"action_type": "finalize_roadmap", "payload": {}}

def run_episode(task_id: str):
    print(f"[START] task={task_id} env=careernav model={MODEL_NAME}")
    
    obs = {}
    done = False
    step = 0
    rewards = []
    score = 0.0
    success = False
    
    try:
        # 1. Reset
        res = requests.post(f"{SERVER_URL}/reset", json={
            "session_id": f"inf_{task_id}",
            "task_id": task_id,
            "cv_path": "overachiever.pdf",
            "seed": 42
        }).json()
        
        obs = res
        
        # 2. Loop
        while not done and step < 10:
            step += 1
            action = get_agent_action(obs, task_id)
            
            step_res = requests.post(f"{SERVER_URL}/step", json={
                "session_id": f"inf_{task_id}",
                "action": action
            }).json()
                
            reward = step_res["reward"]["value"]
            rewards.append(reward)
            done = step_res["done"]
            obs = step_res["observation"]
            error = step_res["info"].get("error")
            
            print(f"[STEP] step={step} action={action.get('action_type', 'unknown')} reward={reward:.2f} done={str(done).lower()} error={error}")

        # 3. End
        score = obs.get("match_score", 0.0)
        # Clamp score to [0.0, 1.0]
        score = max(0.0, min(1.0, score))
        success = score > 0.7
    finally:
        rewards_str = ",".join([f"{r:.2f}" for r in rewards])
        print(f"[END] success={str(success).lower()} steps={step} score={score:.3f} rewards={rewards_str}")

def main():
    if not API_KEY:
        print("Error: API_KEY not set. Please provide HF_TOKEN or API_KEY environmental variables.")
        return
        
    for task in TASKS:
        try:
            run_episode(task)
        except Exception as e:
            print(f"Error executing task {task}: {e}")

if __name__ == "__main__":
    main()
