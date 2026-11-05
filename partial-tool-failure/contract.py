import json


def structured(tools, block, state):
    try:
        data = tools[block.name](**block.input)
        result = {"status": "ok" if data else "empty", "data": data}
    except Exception as e:
        result = {"status": "error", "data": None, "error": str(e)}
    state[block.name] = result["status"]
    state["fails"] = state.get("fails", 0) + (result["status"] != "ok")
    if state["fails"] >= 2:
        state["force"] = {"type": "tool", "name": "submit_answer"}
        result["note"] = (
            "Retry budget used up. Submit your best answer now and say exactly what failed."
        )
    return json.dumps({"tool": block.name, **result})


REQUIRED = ["lookup_account", "get_discount"]
REJECT = "Data is missing, so confidence can't be high. Resubmit with medium or low."
SUBMIT = {
    "name": "submit_answer",
    "description": "Submit your final answer. You must call this to finish.",
    "input_schema": {
        "type": "object",
        "required": ["answer", "confidence"],
        "properties": {
            "answer": {"type": "string"},
            "confidence": {"enum": ["high", "medium", "low"]},
        },
    },
}


def gate(tools, block, state):
    if block.name != "submit_answer":
        return structured(tools, block, state)
    missing = [t for t in REQUIRED if state.get(t) != "ok"]
    if missing and block.input.get("confidence") == "high":
        return json.dumps({"status": "rejected", "missing": missing, "error": REJECT})
    flag = f"\nINCOMPLETE: missing {', '.join(missing)}" if missing else ""
    state["final"] = (
        f"{block.input.get('answer')}\nConfidence: {block.input.get('confidence')}{flag}"
    )
    return "accepted"
