import os, anthropic

client = anthropic.Anthropic()


def list_files(directory="."):
    return "\n".join(os.listdir(directory))


def read_file(path):
    return open(path).read()


TOOLS = [
    {
        "name": "list_files",
        "description": "List files in a directory (defaults to current).",
        "input_schema": {
            "type": "object",
            "properties": {"directory": {"type": "string"}},
        },
    },
    {
        "name": "read_file",
        "description": "Read the full contents of a file at a path.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    },
]

RUNNERS = {"list_files": list_files, "read_file": read_file}


def agent(task):
    messages = [{"role": "user", "content": task}]
    while True:
        reply = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )
        if reply.stop_reason != "tool_use":
            return "".join(b.text for b in reply.content if b.type == "text")

        messages.append({"role": "assistant", "content": reply.content})
        results = []
        for block in reply.content:
            if block.type == "tool_use":
                print(f"-> {block.name} {block.input}")
                out = RUNNERS[block.name](**block.input)
                results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": out}
                )
        messages.append({"role": "user", "content": results})


if __name__ == "__main__":
    print(
        agent(
            "List the files in this folder, read the agent, and explain how its tool loop works."
        )
    )
