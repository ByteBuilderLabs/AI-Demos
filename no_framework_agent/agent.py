from pathlib import Path
from anthropic import AsyncAnthropic

FIXTURES = Path("fixtures")
TASK = "Which of the notes files mentions 'checkpoint', and how many times? Reply with only the number."
client = AsyncAnthropic()


def read_file(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def count_matches(content: str, term: str) -> str:
    return str(content.count(term))


IMPLS = {"read_file": read_file, "count_matches": count_matches}
STR = {"type": "string"}
TOOLS = [
    {
        "name": "read_file",
        "description": "Read one file from the fixtures folder on disk. "
        "Available files: notes_a.txt, notes_b.txt, notes_c.txt.",
        "input_schema": {
            "type": "object",
            "properties": {"name": STR},
            "required": ["name"],
        },
    },
    {
        "name": "count_matches",
        "description": "Count a case sensitive term inside text. The "
        "content argument must be text returned by read_file, never a filename.",
        "input_schema": {
            "type": "object",
            "properties": {"content": STR, "term": STR},
            "required": ["content", "term"],
        },
    },
]


async def run_agent(prompt: str):
    messages = [{"role": "user", "content": prompt}]
    trace = []
    while True:
        resp = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            temperature=0,
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text"), trace

        results = []
        for block in resp.content:
            if block.type == "tool_use":
                trace.append(block.name)
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": IMPLS[block.name](**block.input),
                    }
                )
        messages.append({"role": "user", "content": results})
