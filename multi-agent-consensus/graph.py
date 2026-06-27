from langgraph.graph import StateGraph, START, END
from schemas import DebateState
from nodes import propose, cross_examine, route, judge, finalize

builder = StateGraph(DebateState)
builder.add_node("propose", propose)
builder.add_node("cross_examine", cross_examine)
builder.add_node("judge", judge)
builder.add_node("finalize", finalize)


builder.add_edge(START, "propose")
builder.add_edge("propose", "cross_examine")
builder.add_conditional_edges(
    "cross_examine",
    route,
    {"cross_examine": "cross_examine", "judge": "judge", "finalize": "finalize"},
)
builder.add_edge("judge", END)
builder.add_edge("finalize", END)

graph = builder.compile()


if __name__ == "__main__":
    from nodes import llm

    q = "Which function did Python 3.12 add to run async tasks in batches?"

    print("SINGLE AGENT:", llm.invoke(q).content[:160])

    result = graph.invoke({"question": q, "transcript": [], "round": 0})
    print("\nCONSENSUS:", result["final_answer"])
    print("ROUNDS:", result["round"])

    print("\n--- HOW THEY GOT THERE ---")
    for line in result["transcript"]:
        print(line)
