import httpx
from anthropic import AsyncAnthropic
from tenacity import retry, stop_after_attempt, wait_exponential

MODEL, MAX_STEPS = "claude-haiku-4-5-20251001", 6
TOOL = {
    "name": "lookup_order",
    "description": "Get an order's status by its ID.",
    "input_schema": {
        "type": "object",
        "required": ["order_id"],
        "properties": {"order_id": {"type": "string"}},
    },
}
llm = AsyncAnthropic()
http = httpx.AsyncClient(timeout=2.0)  # the fixture never errors: this is what "fails"


async def fetch(order_id: str) -> str:
    r = await http.get("http://127.0.0.1:8080/lookup", params={"order_id": order_id})
    r.raise_for_status()
    return r.text


async def run_task(question: str, lookup) -> dict:
    msgs = [{"role": "user", "content": question}]
    stats = {"tokens": 0, "ok": False}
    for _ in range(MAX_STEPS):
        r = await llm.messages.create(
            model=MODEL, max_tokens=300, tools=[TOOL], messages=msgs
        )
        stats["tokens"] += r.usage.input_tokens + r.usage.output_tokens
        calls = [b for b in r.content if b.type == "tool_use"]
        if not calls:
            return stats
        results = [await run_tool(c, lookup, stats) for c in calls]
        msgs += [
            {"role": "assistant", "content": r.content},
            {"role": "user", "content": results},
        ]
    return stats


async def run_tool(call, lookup, stats: dict) -> dict:
    try:
        content, is_error = await lookup(call.input["order_id"]), False
        stats["ok"] = True
    except Exception as e:
        content, is_error = f"Tool failed: {type(e).__name__}: {e}", True
    return {
        "type": "tool_result",
        "tool_use_id": call.id,
        "content": content,
        "is_error": is_error,
    }


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
async def naive_lookup(order_id: str) -> str:
    return await fetch(order_id)
