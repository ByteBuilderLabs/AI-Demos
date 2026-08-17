import asyncio, json, os
from anthropic import AsyncAnthropic
from tools import TOOLS, TOOL_SCHEMAS

MODEL, MAX_TURNS, MAX_TOKENS = "claude-sonnet-5", 6, 2048
SYSTEM = "You are a product assistant. Answer using the tools available."
client = AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


async def call_tool(block) -> dict:
    def result(content, is_error=False):
        return {
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": content,
            "is_error": is_error,
        }

    for attempt in (1, 2):
        try:
            return result(
                json.dumps(await TOOLS[block.name](**block.input), default=str)
            )
        except Exception as exc:
            if attempt == 2:
                return result(f"tool error: {exc}", True)


async def run_agent(question: str) -> str:
    messages = [{"role": "user", "content": question}]
    for _ in range(MAX_TURNS):
        reply = await client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM,
            tools=TOOL_SCHEMAS,
            messages=messages,
        )
        calls = [b for b in reply.content if b.type == "tool_use"]
        if not calls:
            return "".join(b.text for b in reply.content if b.type == "text")
        messages.append({"role": "assistant", "content": reply.content})
        results = await asyncio.gather(*(call_tool(b) for b in calls))
        messages.append({"role": "user", "content": list(results)})
    return "max turns reached without a final answer"
