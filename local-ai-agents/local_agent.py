from typing import Annotated, TypedDict
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

llm = ChatOllama(model="llama3.1", temperature=0.0, format="json")


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


@tool
def process_internal_doc(doc_id: str) -> str:
    """Processes a highly sensitive internal document offline."""
    print(f"Processing document {doc_id} securely...")
    return f"Document {doc_id} processed successfully."


tools = [process_internal_doc]
llm_with_tools = llm.bind_tools(tools)


def agent_node(state: AgentState):
    print("Agent is thinking...")
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    messages = state["messages"]
    last_message = messages[-1]

    if last_message.tool_calls:
        return "continue"
    return "end"


workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("action", ToolNode(tools))

workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent", should_continue, {"continue": "action", "end": END}
)
workflow.add_edge("action", "agent")
app = workflow.compile()


if __name__ == "__main__":
    inputs = {"messages": [("user", "Please process document 404.")]}
    for output in app.stream(inputs):
        for key, value in output.items():
            print(f"Node '{key}' finished.")
