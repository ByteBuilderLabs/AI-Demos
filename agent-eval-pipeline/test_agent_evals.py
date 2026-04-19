from langsmith import evaluate
from agent import agent
from evaluators import accuracy_evaluator, tool_use_evaluator


def run_agent(inputs):
    return agent.invoke({"messages": [("user", inputs["question"])]})


def test_agent_regression():
    results = evaluate(
        run_agent,
        data="agent-golden-set",
        evaluators=[accuracy_evaluator, tool_use_evaluator],
        experiment_prefix="ci-run",
    )
    df = results.to_pandas()
    assert df["feedback.accuracy"].mean() >= 0.85
    assert df["feedback.tool_use"].mean() >= 0.90
