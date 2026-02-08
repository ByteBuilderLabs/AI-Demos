from dotenv import load_dotenv

load_dotenv()

import json
from typing import Literal
from langsmith import traceable
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


@tool
def search_docs(query: str) -> str:
    """Search internal documentation for answers."""
    docs = {
        "refund": "Refund policy: 30-day full refund.",
        "pricing": "Plans: Free, Pro ($20/mo), Enterprise.",
        "billing": "Billing cycles are monthly. Contact support.",
    }
    for key, val in docs.items():
        if key in query.lower():
            return val
    return "No relevant documentation found."


@tool
def get_status(service: str) -> str:
    """Check the operational status of a service."""
    if "billing" in service.lower():
        return json.dumps({
            "status": "operational", "healthy": True,
            "details": "p99 latency elevated (4200ms), within SLA"
        })
    return json.dumps({
        "status": "operational", "healthy": True,
        "details": "all systems normal"
    })


tools = [search_docs, get_status]
llm_with_tools = llm.bind_tools(tools)


def call_model(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


graph = StateGraph(MessagesState)
graph.add_node("agent", call_model)
graph.add_node("tools", ToolNode(tools))
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", tools_condition)
graph.add_edge("tools", "agent")
agent = graph.compile()


@traceable(name="HandleUserQuery", metadata={"source": "demo"})
def handle_user_query(user_input: str, user_id: str = "anonymous"):
    result = agent.invoke(
        {"messages": [("user", user_input)]},
        config={"metadata": {"user_id": user_id}},
    )
    return result["messages"][-1].content


if __name__ == "__main__":
    # Clean run — baseline
    print("--- Query 1 ---")
    r1 = handle_user_query("What is the refund policy?", user_id="user_42")
    print(r1)

    # Buggy run — triggers ambiguous tool response
    print("\n--- Query 2 ---")
    r2 = handle_user_query("Is the billing service having issues?", user_id="user_42")
    print(r2)
