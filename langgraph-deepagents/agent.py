import os
from typing import Literal
from dotenv import load_dotenv
from tavily import TavilyClient
from deepagents import create_deep_agent

load_dotenv()

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search to find information on a topic."""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )


research_instructions = """You are an expert researcher.

## Workflow
1. Use write_todos to plan your research steps before doing anything.
2. Use internet_search to gather information from multiple sources.
3. Use write_file to save intermediate findings as you go.
4. Synthesize everything into a clear, well-structured report.

Always cite your sources. If information conflicts across sources,
note the discrepancy and explain which source is more reliable.
"""


verification_subagent = {
    "name": "fact-checker",
    "description": "Verify claims by cross-referencing multiple sources",
    "system_prompt": (
        "You verify factual claims. Search for corroborating "
        "or contradicting evidence. Return a short verdict: "
        "confirmed, disputed, or unverified, with source URLs."
    ),
    "tools": [internet_search],
}


agent = create_deep_agent(
    model="openai:gpt-4o",
    tools=[internet_search],
    system_prompt=research_instructions,
    subagents=[verification_subagent],
)


def print_chunk(namespace, data):
    node = list(data.keys())[0]
    if "Middleware" in node or "before_agent" in node:
        return
    prefix = "[subagent]" if namespace else "[agent]"

    if node == "model":
        msg = data["model"]["messages"][0]
        if msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"{prefix} 🔧 {tc['name']}({tc['args']})")
        elif hasattr(msg, "content"):
            text = msg.content
            if isinstance(text, list):
                text = next(
                    (
                        b["text"]
                        for b in text
                        if isinstance(b, dict) and b.get("type") == "text"
                    ),
                    None,
                )
            if text:
                print(f"\n{prefix} 💬 Response:\n{text}\n")

    elif node == "tools":
        if "todos" in data["tools"]:
            print(f"{prefix} 📋 TODOs updated:")
            for t in data["tools"]["todos"]:
                icon = "✅" if t["status"] == "completed" else "⏳"
                print(f"  {icon} {t['content']}")
        if "files" in data["tools"] and data["tools"]["files"]:
            for path in data["tools"]["files"]:
                print(f"{prefix} 📁 Wrote file: {path}")


query = "What are the latest breakthroughs in quantum computing in 2026?"

for namespace, data in agent.stream(
    {"messages": [{"role": "user", "content": query}]},
    stream_mode="updates",
    subgraphs=True,
):
    print_chunk(namespace, data)
