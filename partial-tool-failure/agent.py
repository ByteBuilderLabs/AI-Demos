import json
import anthropic

client = anthropic.Anthropic(max_retries=5)
MODEL = "claude-haiku-5-5"
SYSTEM = "You are a billing assistant. Use the tools, and always use calculate for arithmetic."
SCHEMAS = json.load(open("schemas.json"))


def naive(tools, block, state):
    try:
        return json.dumps(tools[block.name](**block.input))
    except Exception as e:
        return f"Error: {e}"


def run_agent(question, tools, handle=naive, schemas=SCHEMAS, choice="auto"):
    messages, state = [{"role": "user", "content": question}], {}
    for _ in range(10):
        resp = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM,
            messages=messages,
            tools=schemas,
            tool_choice=state.get("force", {"type": choice}),
        )
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")
        results = [
            {
                "type": "tool_result",
                "tool_use_id": b.id,
                "content": handle(tools, b, state),
            }
            for b in resp.content
            if b.type == "tool_use"
        ]
        if "final" in state:
            return state["final"]
        messages.append({"role": "user", "content": results})
    return "Incomplete: the agent ran out of turns."
