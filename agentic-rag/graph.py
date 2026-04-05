from langgraph.graph import StateGraph, END
from state import GraphState
from nodes import decompose, retrieve_and_grade, synthesize


def should_continue(state: GraphState) -> str:
    for sq in state["sub_queries"]:
        if not sq.is_relevant and sq.retry_count < 2:
            return "retrieve_and_grade"
    return "synthesize"


graph = StateGraph(GraphState)
graph.add_node("decompose", decompose)
graph.add_node("retrieve_and_grade", retrieve_and_grade)
graph.add_node("synthesize", synthesize)


graph.set_entry_point("decompose")
graph.add_edge("decompose", "retrieve_and_grade")
graph.add_conditional_edges(
    "retrieve_and_grade",
    should_continue,
    {"retrieve_and_grade": "retrieve_and_grade", "synthesize": "synthesize"},
)
graph.add_edge("synthesize", END)
app = graph.compile()


if __name__ == "__main__":
    result = app.invoke(
        {
            "original_query": "How does LangGraph manage state and how does self-corrective RAG improve retrieval?",
            "sub_queries": [],
            "final_answer": "",
        }
    )
    print(result["final_answer"])
