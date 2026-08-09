import asyncio
from fastapi import FastAPI
from tool import call_vendor

SLOTS = asyncio.Semaphore(4)
STATE = {"busy": 0, "queued": 0}
app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    return STATE


@app.get("/run")
async def run_tool(path: str = "/ok"):
    STATE["queued"] += 1
    async with SLOTS:
        STATE["queued"] -= 1
        STATE["busy"] += 1
        try:
            return {"result": await asyncio.to_thread(call_vendor, path)}
        finally:
            STATE["busy"] -= 1
