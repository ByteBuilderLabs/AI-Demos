import os
import operator
from typing import Annotated, TypedDict, List, Union

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

# Load environment variables for API keys
load_dotenv()


class AgentState(TypedDict):
    # The operator.add reducer ensures messages are appended, not replaced
    messages: Annotated[List[BaseMessage], operator.add]


@tool
def search_web(query: str):
    """Searches the web for real-time information."""
    # Production note: Swap this mock for a Tavily or Serper API call
    return f"Search result for '{query}': LangGraph is a library for building stateful, multi-actor AI."


tools = [search_web]
model = ChatOpenAI(model="gpt-4o", temperature=0).bind_tools(tools)


# The reasoning node
def call_model(state: AgentState):
    response = model.invoke(state["messages"])
    return {"messages": [response]}


# The action node (prebuilt utility)
tool_node = ToolNode(tools)


workflow = StateGraph(AgentState)

workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)


def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]

    # If the LLM made a tool call, we continue to the action node
    if last_message.tool_calls:
        return "continue"
    # Otherwise, we stop
    return "end"


workflow.add_edge(START, "agent")

workflow.add_conditional_edges(
    "agent", should_continue, {"continue": "action", "end": END}
)

# Crucial: The cycle back to the agent for post-action reasoning
workflow.add_edge("action", "agent")

# Compile the graph into an executable application
app = workflow.compile()


# Define the entry point for the test
inputs = {"messages": [HumanMessage(content="What is LangGraph?")]}

print("\n--- [START] Bypassing Linear Constraints ---")

# app.stream yields a dictionary for each node that finishes execution
for output in app.stream(inputs):
    # key = node name, value = what that node returned
    for key, value in output.items():
        print(f"\n[NODE COMPLETED]: {key}")
        # Inspecting the messages added to the state
        for message in value.get("messages", []):
            if hasattr(message, "tool_calls") and message.tool_calls:
                print(f"Decision: Calling Tool '{message.tool_calls[0]['name']}'")
            else:
                print(f"Content: {message.content[:100]}...")
    print("-" * 40)

print("\n--- [END] Goal Reached ---")
