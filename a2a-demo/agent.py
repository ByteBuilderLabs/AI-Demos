from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class ResearchState(TypedDict):
    query: str
    result: str

def research_node(state: ResearchState) -> ResearchState:
    llm = ChatOpenAI(model="gpt-4o-mini")
    response = llm.invoke(
        f"Research this topic concisely: {state['query']}"
    )
    return {"query": state["query"], "result": response.content}

graph = StateGraph(ResearchState)
graph.add_node("research", research_node)
graph.add_edge(START, "research")
graph.add_edge("research", END)
research_agent = graph.compile()