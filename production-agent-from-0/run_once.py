import asyncio
from agent import TASK, run_agent

print(asyncio.run(run_agent(TASK)))
