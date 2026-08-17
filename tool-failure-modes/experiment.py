import asyncio, os
from collections import Counter
from agent import run_agent
from oracle import classify

RUNS, EXPECTED = 50, "249"
GATE = asyncio.Semaphore(10)
QUESTION = "What does SKU A-1001 cost, and is it over 200 dollars?"


async def one_run() -> str:
    async with GATE:
        try:
            return classify(await run_agent(QUESTION), EXPECTED, False)
        except Exception as exc:
            print(repr(exc))
            return classify("", EXPECTED, True)


MODES = ["raise", "malformed", "empty", "slow"]


async def main():
    os.environ["FAULT_MODE"] = "none"
    assert EXPECTED in await run_agent(QUESTION), "clean run failed"
    for mode in MODES:
        os.environ["FAULT_MODE"] = mode
        results = await asyncio.gather(*[one_run() for _ in range(RUNS)])
        print(f"{mode:<10} {dict(Counter(results))}")


asyncio.run(main())
