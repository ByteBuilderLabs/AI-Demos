import asyncio, random, time
from fastapi import FastAPI

app = FastAPI()
BASE, PER_INFLIGHT = 0.4, 0.10  # base latency + extra seconds per in-flight request
state = {"in_flight": 0, "requests": 0}


@app.get("/stats")
async def stats():
    return state


@app.get("/lookup")
async def lookup(order_id: str):
    state["requests"] += 1
    state["in_flight"] += 1
    t = time.monotonic() - state.setdefault("t0", time.monotonic())
    hiccup = (
        5 if 15 <= t < 20 else 1
    )  # a five-second slowdown: deploy, GC pause, noisy neighbor
    try:  # client timeouts don't cancel this, so abandoned work still holds capacity
        delay = (
            (BASE + PER_INFLIGHT * state["in_flight"])
            * hiccup
            * random.uniform(0.6, 1.6)
        )
        await asyncio.sleep(delay)
        return {"order_id": order_id, "status": "shipped"}
    finally:
        state["in_flight"] -= 1
