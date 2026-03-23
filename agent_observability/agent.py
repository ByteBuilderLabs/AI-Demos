from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langfuse.langchain import CallbackHandler
from observability import observe_node, langfuse
from typing import TypedDict

langfuse_handler = CallbackHandler()
llm = ChatOpenAI(model="gpt-4o-mini")

class AgentState(TypedDict):
    query: str
    research: str
    summary: str

@observe_node("research")
def research_node(state: AgentState):
    response = llm.invoke(
        f"Research this topic: {state['query']}",
        config={"callbacks": [langfuse_handler]}
    )
    return {**state, "research": response.content}


@observe_node("summarize")
def summarize_node(state: AgentState):
    response = llm.invoke(
        f"Summarize this concisely: {state['research']}",
        config={"callbacks": [langfuse_handler]}
    )
    return {**state, "summary": response.content}

graph = StateGraph(AgentState)
graph.add_node("research", research_node)
graph.add_node("summarize", summarize_node)
graph.add_edge(START, "research")
graph.add_edge("research", "summarize")
graph.add_edge("summarize", END)
agent = graph.compile()