import os
import requests
import json
import time
import traceback
from openai import OpenAI
from typing import List, Dict, Any

# Environment & Model Config
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    print("Error: API_KEY not set.")
    exit(1)

# Sanitize Base URL (Ensure it has a scheme)
if API_BASE_URL and not API_BASE_URL.startswith("http"):
    API_BASE_URL = f"https://{API_BASE_URL}"

# Default Server Discovery List
POSSIBLE_URLS = [
    os.getenv("CAREERNAV_URL"),
    "http://localhost:7860",
    "http://env:7860",
    "http://127.0.0.1:7860"
]
POSSIBLE_URLS = [url for url in POSSIBLE_URLS if url]

SERVER_URL = POSSIBLE_URLS[0] if POSSIBLE_URLS else "http://localhost:7860"

print(f"--- Diagnostic Info ---")
print(f"MODEL_NAME: {MODEL_NAME}")
print(f"API_BASE_URL: {API_BASE_URL}")
if API_KEY:
    masked_key = f"{API_KEY[:4]}...{API_KEY[-4:]}" if len(API_KEY) > 8 else "****"
    print(f"API_KEY: {masked_key}")
else:
    print(f"API_KEY: NOT FOUND")
print(f"-----------------------")

import httpx
client = OpenAI(
    api_key=API_KEY,
    base_url=API_BASE_URL,
    http_client=httpx.Client(
        timeout=30.0
    )
)

TASKS = [
    "skill_gap_identifier",
    "course_recommender",
    "full_optimizer",
    "pm_scheme_matcher"
]

def wait_for_server():
    global SERVER_URL
    print("Searching for healthy server...")
    
    start_time = time.time()
    while time.time() - start_time < 30: # 30s timeout
        for url in POSSIBLE_URLS:
            try:
                res = requests.get(f"{url}/health", timeout=1)
                if res.status_code == 200:
                    SERVER_URL = url
                    print(f"Success! Server found and healthy at: {SERVER_URL}")
                    return True
            except:
                continue
        time.sleep(1)
        
    print(f"Warning: No healthy server found after 30s. Proceeding with: {SERVER_URL}")
    return False

def get_agent_action(obs: Dict[str, Any], task_id: str) -> Dict[str, Any]:
    if not client:
        return {"action_type": "finalize_roadmap", "payload": {"justification": "Fallback due to Missing Client"}}

    prompt = f"""
    You are an AI Career Coach in the CareerNav environment.
    Task: {task_id}
    Current Observation: {json.dumps(obs, indent=2)}
    
    Goal:
    1. Identify ALL missing skills from the student's profile using 'flag_gap'.
    2. Once all gaps are identified, recommend the best courses from the catalog using 'recommend_course'.
    3. Before finishing, check eligibility for relevant government schemes using 'check_scheme_eligibility' to maximize score.
    4. Only when the roadmap is optimized and schemes are checked, use 'finalize_roadmap'.
    
    Strategy: Do NOT finalize before at least 5-8 steps to ensure thoroughness.
    
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
            timeout=30,
            user="careernav-agent" # Recommended for LiteLLM proxy tracking
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
        }, timeout=15)
        reset_res.raise_for_status()
        obs = reset_res.json()
        
        # 2. Loop
        while not done and step < 15:
            step += 1
            action = get_agent_action(obs, task_id)
            
            step_res = requests.post(f"{SERVER_URL}/step", json={
                "session_id": f"inf_{task_id}",
                "action": action
            }, timeout=15)
            step_res.raise_for_status()
            
            try:
                data = step_res.json()
            except Exception as e:
                print(f"Failed to parse JSON response: {step_res.text[:100]}...")
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
    # Wait for environmental stability (evaluators start server and agent simultaneously)
    wait_for_server()
    
    for task in TASKS:
        try:
            run_episode(task)
        except Exception as e:
            print(f"Unhandled error in task {task}: {e}")

if __name__ == "__main__":
    main()
