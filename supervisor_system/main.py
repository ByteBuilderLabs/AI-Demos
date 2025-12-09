from typing import Annotated, List, TypedDict, Literal
import operator
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

load_dotenv()


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next: str


llm = ChatOpenAI(model="gpt-4o-mini")


def create_agent_node(agent_name, system_prompt):
    def agent_node(state):
        messages = state["messages"]
        response = llm.invoke([SystemMessage(content=system_prompt)] + messages)
        return {"messages": [response]}

    return agent_node


researcher_node = create_agent_node(
    "Researcher", "You are a researcher. Provide accurate data and facts. Be concise."
)

coder_node = create_agent_node(
    "Coder",
    "You are a Python expert. Write executed code based on data. Output only code.",
)


class SupervisorDecision(BaseModel):
    next: Literal["Researcher", "Coder", "FINISH"]


system_prompt = (
    "You are a supervisor. Manage the conversation between workers."
    "Given the user request, decide who should act next."
    "If the task is finished, return FINISH."
)


def supervisor_node(state):
    messages = state["messages"]

    chain = llm.with_structured_output(SupervisorDecision)
    decision = chain.invoke([SystemMessage(content=system_prompt)] + messages)

    return {"next": decision.next}


workflow = StateGraph(AgentState)

workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("Researcher", researcher_node)
workflow.add_node("Coder", coder_node)


workflow.set_entry_point("Supervisor")
workflow.add_edge("Researcher", "Supervisor")
workflow.add_edge("Coder", "Supervisor")

workflow.add_conditional_edges(
    "Supervisor",
    lambda x: x["next"],
    {"Researcher": "Researcher", "Coder": "Coder", "FINISH": END},
)

app = workflow.compile()

if __name__ == "__main__":
    final_state = app.invoke(
        {
            "messages": [
                HumanMessage(
                    content="""Find the GDP of France for the last 3 years 
                         and write a Python script to plot it."""
                )
            ]
        }
    )

    print("\n--- FINAL OUTPUT ---\n")
    print(final_state["messages"][-1].content)
