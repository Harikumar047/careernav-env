from fastapi import FastAPI, HTTPException
from careernav.env import CareerNavEnv
from careernav.models import Observation, Action, Reward, StepInfo
from pydantic import BaseModel
from typing import Dict, Any, Optional

app = FastAPI(title="CareerNav-Env OpenEnv API")

sessions = {}

class ResetRequest(BaseModel):
    session_id: str = "default"
    cv_path: str = "lazy.pdf"
    target_role: str = "Software Engineer"
    task_id: str = "default"
    seed: int = 42
    
class StepRequest(BaseModel):
    session_id: str = "default"
    action: Action

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reset", response_model=Observation)
def reset(req: ResetRequest):
    env = CareerNavEnv()
    sessions[req.session_id] = env
    obs = env.reset(cv_path=req.cv_path, target_role=req.target_role, seed=req.seed)
    return obs

@app.post("/step")
def step(req: StepRequest) -> Dict[str, Any]:
    if req.session_id not in sessions:
        raise HTTPException(status_code=400, detail="Session not initialized via /reset")
    
    env = sessions[req.session_id]
    obs, reward, done, info = env.step(req.action)
    
    return {
        "observation": obs.model_dump(),
        "reward": reward.model_dump(),
        "done": done,
        "info": info.model_dump()
    }

@app.get("/state", response_model=Observation)
def state(session_id: str = "default") -> Observation:
    if session_id not in sessions:
        raise HTTPException(status_code=400, detail="Session not initialized via /reset")
    return sessions[session_id].state()

def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
