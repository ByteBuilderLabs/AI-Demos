from fastapi import FastAPI
from celery.result import AsyncResult
from worker import run_research_agent, celery_app

app = FastAPI()


@app.post("/api/research")
async def start_research(prompt: str):
    task = run_research_agent.delay(prompt)
    return {"task_id": task.id}


@app.get("/api/research/{task_id}")
async def get_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)

    if not task_result.ready():
        return {"status": task_result.state}

    return {"status": task_result.state, "result": task_result.result}
