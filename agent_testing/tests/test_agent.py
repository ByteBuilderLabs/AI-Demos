import pytest
from langsmith import evaluate
from agent.graph import run_agent
from evaluators.checks import (
    tool_call_evaluator,
    argument_evaluator,
    answer_evaluator,
)


def test_agent_regression_suite():
    results = evaluate(
        run_agent,
        data="agent-regression-suite",
        evaluators=[
            tool_call_evaluator,
            argument_evaluator,
            answer_evaluator,
        ],
        experiment_prefix="regression",
    )
    df = results.to_pandas()
    for col in ["correct_tool", "correct_args", "answer_contains"]:
        assert (
            df[f"feedback.{col}"].min() == 1
        ), f"Evaluator '{col}' failed on at least one example"
