from fastapi import FastAPI, Request
import json

app = FastAPI()

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    task_id = body['messages'][0]['content'] # Simplified extraction
    
    # Simple logic to return task-specific JSON responses
    if "skill_gap_identifier" in task_id:
        content = '{"action_type": "flag_gap", "payload": {"skill": "Cloud Architecture", "justification": "Missing from CV"}}'
    elif "course_recommender" in task_id:
        content = '{"action_type": "recommend_course", "payload": {"course_name": "AWS Certified Solutions Architect", "provider": "Coursera"}}'
    elif "pm_scheme_matcher" in task_id:
        content = '{"action_type": "check_scheme_eligibility", "payload": {"scheme_id": "PM-KAUSHAL-VIKAS", "eligibility": "High"}}'
    else:
        content = '{"action_type": "finalize_roadmap", "payload": {"justification": "Optimization complete"}}'
        
    return {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": content
                }
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
