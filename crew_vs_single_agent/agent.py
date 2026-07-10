import anthropic
from tools import read_file, write_file, verify

client = anthropic.Anthropic()

SYSTEM_PROMPT = (
    "You turn source docs into one report. Plan the work, extract the "
    "required fields, assemble them, then call verify and fix whatever "
    "it flags before you finish. Use read_file, write_file, and verify."
)

DISPATCH = {"read_file": read_file, "write_file": write_file, "verify": verify}


def tool(name, desc, props):
    return {
        "name": name,
        "description": desc,
        "input_schema": {
            "type": "object",
            "properties": {p: {"type": "string"} for p in props},
            "required": props,
        },
    }


TOOLS = [
    tool("read_file", "Read a source doc, return its text.", ["path"]),
    tool("write_file", "Save the final report to a path.", ["path", "content"]),
    tool("verify", "Score the report against the rubric.", ["path"]),
]


def run(task: str) -> int:
    messages = [{"role": "user", "content": task}]
    total = 0
    for _ in range(12):
        resp = client.messages.create(
            model="claude-sonnet-5",  # [VERIFY] exact API string for Sonnet 5
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )
        total += resp.usage.input_tokens + resp.usage.output_tokens
        if resp.stop_reason != "tool_use":
            return total
        messages.append({"role": "assistant", "content": resp.content})
        results = [
            {
                "type": "tool_result",
                "tool_use_id": b.id,
                "content": str(DISPATCH[b.name](**b.input)),
            }
            for b in resp.content
            if b.type == "tool_use"
        ]
        messages.append({"role": "user", "content": results})
    return total
