from langchain_openai import ChatOpenAI
from schemas import AccuracyScore

judge = ChatOpenAI(model="gpt-4o-mini").with_structured_output(AccuracyScore)


def accuracy_evaluator(run, example):
    actual = run.outputs["messages"][-1].content
    expected = example.outputs["answer"]
    prompt = (
        f"Expected answer: {expected}\n"
        f"Actual answer: {actual}\n"
        f"Score the match from 0 to 1 and briefly explain."
    )
    result = judge.invoke(prompt)
    return {"key": "accuracy", "score": result.score, "comment": result.reasoning}


def tool_use_evaluator(run, example):
    expected_tool = example.outputs["expected_tool"]
    messages = run.outputs.get("messages", [])
    tool_calls = []
    for msg in messages:
        calls = getattr(msg, "tool_calls", None) or []
        for tc in calls:
            name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
            if name:
                tool_calls.append(name)
    correct = expected_tool in tool_calls
    return {"key": "tool_use", "score": 1.0 if correct else 0.0}
