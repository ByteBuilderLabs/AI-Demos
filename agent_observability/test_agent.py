from langfuse import observe, get_client
from agent import agent

langfuse = get_client()

@observe(name="test-run")
def run_agent():
    result = agent.invoke({"query": "What are the key trends in AI agents for 2026?"})
    print(result["summary"])
    return result

run_agent()
langfuse.flush()