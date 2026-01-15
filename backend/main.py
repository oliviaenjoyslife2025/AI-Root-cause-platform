from fastapi import FastAPI, BackgroundTasks, HTTPException
import asyncio
import aioredis
from typing import Dict
from ai_engine.agent import run_rca
import uuid

app = FastAPI(title="AI-Root-cause-platform API (Aura-Ops)")

# Redis configuration
REDIS_URL = "redis://localhost:6379"
redis = None

@app.on_event("startup")
async def startup():
    global redis
    try:
        redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
    except Exception as e:
        print(f"Redis not available: {e}")

async def process_rca_task(incident_id: str):
    """Background task to run AI Agent and store results in Redis."""
    print(f"🚀 Starting AI RCA for {incident_id}...")
    await redis.set(f"incident:{incident_id}:status", "processing")
    
    try:
        # Run the LangGraph Agent
        result = await run_rca(incident_id)
        
        # Save results to Redis
        await redis.set(f"incident:{incident_id}:status", "completed")
        await redis.set(f"incident:{incident_id}:result", str(result['suggested_fix']))
        print(f"✅ RCA for {incident_id} completed.")
    except Exception as e:
        await redis.set(f"incident:{incident_id}:status", f"failed: {str(e)}")
        print(f"❌ RCA for {incident_id} failed: {e}")

@app.get("/")
async def root():
    return {"message": "AI-Root-cause-platform (Aura-Ops) is online"}

@app.post("/v1/incidents/report")
async def report_incident(incident_data: Dict, background_tasks: BackgroundTasks):
    incident_id = str(uuid.uuid4())[:8]
    # Trigger AI Agent in background
    background_tasks.add_task(process_rca_task, incident_id)
    return {
        "status": "accepted", 
        "incident_id": incident_id,
        "message": "AI RCA analysis triggered in background."
    }

@app.get("/v1/incidents/{incident_id}/status")
async def get_incident_status(incident_id: str):
    if not redis:
        raise HTTPException(status_code=500, detail="Redis connection not established")
        
    status = await redis.get(f"incident:{incident_id}:status")
    result = await redis.get(f"incident:{incident_id}:result")
    
    return {
        "incident_id": incident_id, 
        "status": status or "not_found",
        "analysis_result": result
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
