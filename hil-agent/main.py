import os
import operator
from typing import TypedDict, Annotated, List
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()


class AgentState(TypedDict):
    # 'operator.add' ensures we append to history, not overwrite it
    messages: Annotated[List[BaseMessage], operator.add]


llm = ChatOpenAI(model="gpt-4o", temperature=0)


def reason_step(state: AgentState):
    print("--- [NODE] REASONING ---")
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}


def sensitive_action_step(state: AgentState):
    print("--- [NODE] EXECUTING SENSITIVE ACTION ---")
    print(">> EXECUTING TRANSFER OF $500...")
    return {"messages": [SystemMessage(content="Transfer Complete.")]}


# 1. Initialize
builder = StateGraph(AgentState)

# 2. Add Nodes
builder.add_node("reason", reason_step)
builder.add_node("action", sensitive_action_step)

# 3. Add Edges
builder.set_entry_point("reason")
builder.add_edge("reason", "action")
builder.add_edge("action", END)

# 4. Persistence
memory = MemorySaver()

# 5. Compile with Safety Valve
graph = builder.compile(
    checkpointer=memory, interrupt_before=["action"]  # <--- The Guardrail
)


thread_config = {"configurable": {"thread_id": "byte_builder_demo_1"}}

initial_input = {"messages": [HumanMessage(content="Transfer $500 to Account B")]}

print("--- STARTING RUN ---")

# First Run: Will stop before 'action'
for event in graph.stream(initial_input, thread_config):
    for k, v in event.items():
        print(f"Finished Node: {k}")

print("\n--- PROCESS PAUSED. WAITING FOR APPROVAL ---")
approval = input("Approve transfer? (y/n): ")

if approval.lower() == "y":
    print("\n--- RESUMING EXECUTION ---")

    # Passing None resumes from the saved state
    for event in graph.stream(None, thread_config):
        for k, v in event.items():
            print(f"Finished Node: {k}")
else:
    print("--- ACTION REJECTED ---")
