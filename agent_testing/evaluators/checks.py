from langsmith.schemas import Run, Example


def tool_call_evaluator(run: Run, example: Example) -> dict:
    expected = example.outputs["expected"]
    messages = run.outputs.get("messages", [])
    ai_messages = [m for m in messages if hasattr(m, "tool_calls") and m.tool_calls]
    if not ai_messages:
        return {"key": "correct_tool", "score": 0}
    called_tool = ai_messages[0].tool_calls[0]["name"]
    return {
        "key": "correct_tool",
        "score": int(called_tool == expected["tool"]),
    }


def argument_evaluator(run: Run, example: Example) -> dict:
    expected = example.outputs["expected"]
    messages = run.outputs.get("messages", [])
    ai_messages = [m for m in messages if hasattr(m, "tool_calls") and m.tool_calls]
    if not ai_messages:
        return {"key": "correct_args", "score": 0}
    actual_args = ai_messages[0].tool_calls[0]["args"]
    expected_args = expected.get("args", {})
    all_match = all(
        str(actual_args.get(k, "")).lower() == str(v).lower()
        for k, v in expected_args.items()
    )
    return {"key": "correct_args", "score": int(all_match)}


def answer_evaluator(run: Run, example: Example) -> dict:
    expected = example.outputs["expected"]
    output = run.outputs.get("output", "")
    contains = expected.get("answer_contains", "")
    return {
        "key": "answer_contains",
        "score": int(contains.lower() in output.lower()),
    }
