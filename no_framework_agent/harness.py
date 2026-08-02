import asyncio
from collections import Counter
from agent import TASK, run_agent

EXPECTED = "4"


def check(answer: str, trace: list[str]) -> str:
    if answer.strip() != EXPECTED:
        return "fail:answer"
    if not trace or trace[0] != "read_file" or trace[-1] != "count_matches":
        return "fail:trace"
    return "pass"


async def one_run() -> str:
    try:
        answer, trace = await run_agent(TASK)
    except Exception as e:
        return f"fail:error {type(e).__name__}"
    outcome = check(answer, trace)
    if outcome != "pass":
        print(f"  {outcome}: {answer!r} {trace}")
    return outcome


async def main():
    outcomes = await asyncio.gather(*(one_run() for _ in range(50)))
    print(Counter(outcomes))


asyncio.run(main())
