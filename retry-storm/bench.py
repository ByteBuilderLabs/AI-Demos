import asyncio, statistics, sys, time
import agent


async def one_task(i: int, lookup, rate: int) -> dict:
    await asyncio.sleep(i / rate)  # open loop: arrivals never wait for the service
    start = time.monotonic()
    try:
        stats = await agent.run_task(f"What's the status of order {1000 + i}?", lookup)
    except Exception:  # an LLM-side error is a failed task, not a crashed benchmark
        stats = {"tokens": 0, "ok": False}
    return {**stats, "secs": time.monotonic() - start}


async def main(arm: str, rate=4, duration=60):
    if arm == "guarded":  # lazy import: guards.py doesn't exist yet on the first run
        from guards import guarded_lookup as lookup
    else:
        lookup = agent.naive_lookup
    results = await asyncio.gather(
        *(one_task(i, lookup, rate) for i in range(rate * duration))
    )
    served = (await agent.http.get("http://127.0.0.1:8080/stats")).json()["requests"]
    p95 = statistics.quantiles([r["secs"] for r in results], n=20)[-1]
    ok = sum(r["ok"] for r in results) / len(results)
    tokens = sum(r["tokens"] for r in results)
    print(
        f"{arm}: tasks={len(results)} dependency_requests={served} "
        f"success={ok:.0%} p95={p95:.1f}s tokens={tokens:,}"
    )


asyncio.run(main(sys.argv[1]))
