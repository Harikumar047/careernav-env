import os
import requests
import json
import traceback
from openai import OpenAI
from typing import List, Dict, Any

# Environment & Model Config
# The platform provides API_BASE_URL and API_KEY. We must use them to pass LLM Criteria Check.
API_BASE_URL = os.getenv("API_BASE_URL") or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1"
API_KEY = os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("HF_TOKEN")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

# Default to localhost for evaluation environments
SERVER_URL = os.getenv("CAREERNAV_URL", "http://localhost:7860")

print(f"--- Diagnostic Info ---")
print(f"MODEL_NAME: {MODEL_NAME}")
print(f"API_BASE_URL: {API_BASE_URL}")
if API_KEY:
    masked_key = f"{API_KEY[:4]}...{API_KEY[-4:]}" if len(API_KEY) > 8 else "****"
    print(f"API_KEY: {masked_key}")
else:
    print(f"API_KEY: NOT FOUND (This will likely fail LLM Criteria Check)")
print(f"-----------------------")

client = None
if API_KEY and API_BASE_URL:
    try:
        # Strictly following platform instructions to use provided base_url and api_key
        client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)
        print("Success: OpenAI client initialized via Proxy.")
    except Exception as e:
        print(f"Critical Error: Failed to initialize OpenAI client: {e}")
        # traceback.print_exc()
        client = None
else:
    print("Warning: Missing API_KEY or API_BASE_URL. Using fallback behavior.")

TASKS = [
    "skill_gap_identifier",
    "course_recommender",
    "full_optimizer",
    "pm_scheme_matcher"
]

def get_agent_action(obs: Dict[str, Any], task_id: str) -> Dict[str, Any]:
    if not client:
        # Fallback action to prevent crashing if LLM is unavailable
        return {"action_type": "finalize_roadmap", "payload": {"justification": "Fallback due to Missing Client"}}

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
            messages=[{"role": "user", "content": prompt}],
            timeout=30
        )
        content = response.choices[0].message.content
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        return json.loads(content)
    except Exception as e:
        print(f"Error in LLM call: {e}")
        return {"action_type": "finalize_roadmap", "payload": {"justification": f"LLM Error: {str(e)}"}}

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
        reset_res = requests.post(f"{SERVER_URL}/reset", json={
            "session_id": f"inf_{task_id}",
            "task_id": task_id,
            "cv_path": "overachiever.pdf",
            "seed": 42
        }, timeout=10)
        reset_res.raise_for_status()
        obs = reset_res.json()
        
        # 2. Loop
        while not done and step < 10:
            step += 1
            action = get_agent_action(obs, task_id)
            
            step_res = requests.post(f"{SERVER_URL}/step", json={
                "session_id": f"inf_{task_id}",
                "action": action
            }, timeout=10)
            step_res.raise_for_status()
            
            try:
                data = step_res.json()
            except Exception as e:
                print(f"Failed to parse JSON response: {step_res.text}")
                break
                
            reward = data["reward"]["value"]
            rewards.append(reward)
            done = data["done"]
            obs = data["observation"]
            error = data["info"].get("error")
            
            print(f"[STEP] step={step} action={action.get('action_type', 'unknown')} reward={reward:.2f} done={str(done).lower()} error={error}")

        # 3. End
        score = obs.get("match_score", 0.0)
        score = max(0.0, min(1.0, score))
        success = score > 0.7
    except Exception as e:
        print(f"Episode failed with error: {e}")
    finally:
        rewards_str = ",".join([f"{r:.2f}" for r in rewards])
        print(f"[END] success={str(success).lower()} steps={step} score={score:.3f} rewards={rewards_str}")

def main():
    for task in TASKS:
        try:
            run_episode(task)
        except Exception as e:
            print(f"Unhandled error in task {task}: {e}")

if __name__ == "__main__":
    main()
