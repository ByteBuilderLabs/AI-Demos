import os
import operator
from typing import Annotated, List, TypedDict, Union

from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
load_dotenv()

# Model Setup: Orchestrator vs. Worker
planner = ChatOpenAI(model="o1") # The Brain
fast_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0) # The Grader
search_tool = TavilySearch(max_results=3) # The Eyes


class AgentState(TypedDict):
    # 'operator.add' ensures the conversation history is cumulative
    messages: Annotated[List[BaseMessage], operator.add]
    # Boolean flag to control the verification loop
    is_verified: bool
    # Temporary storage for research findings
    context: List[str]
    

def research_planner(state: AgentState):
    print("---LOG: PLANNING STRATEGY---")
    query = state['messages'][0].content
    # o1 generates a multi-step search plan
    plan = planner.invoke([HumanMessage(content=f"Create a search plan for: {query}. Always keep it under 200 characters long.")])
    return {"messages": [plan]}


def web_researcher(state: AgentState):
    print("---LOG: EXECUTING SEARCH---")
    query = state['messages'][-1].content
    results = search_tool.invoke({"query": query})
    content = "\n".join(r['content'] for r in results['results'])
    return {"context": [content]}


def critic(state: AgentState):
    print("---LOG: VERIFYING DATA---")
    # Grade the context against the original query
    context = "\n".join(state['context'])
    prompt = f"Does this data answer the user question? If not, say 'INCOMPLETE', if it does say 'COMPLETE'. Data: {context}"
    verification = fast_llm.invoke([HumanMessage(content=prompt)])
    
    is_verified = "INCOMPLETE" not in verification.content.upper()
    return {"is_verified": is_verified, "messages": [verification]}


workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("planner", research_planner)
workflow.add_node("researcher", web_researcher)
workflow.add_node("critic", critic)

# Define Flow
workflow.add_edge(START, "planner")
workflow.add_edge("planner", "researcher")
workflow.add_edge("researcher", "critic")

# The Verification Loop
workflow.add_conditional_edges(
    "critic",
    lambda x: "planner" if not x["is_verified"] else END
)

# Compile & Test
app = workflow.compile()
print("Graph Ready. Initializing Research Loop...")

# Run a sample query
inputs = {"messages": [HumanMessage(content="What are the latest benchmarks for o1 vs gpt-4o?")]}
for output in app.stream(inputs):
    print(output)