import json
import pytest
from dataset import QA

answers = {a["q"]: a["model_answer"] for a in json.load(open("answers.json"))}
reference = {item["q"]: item["answer"] for item in QA}


def normalize(text):
    return "".join(c for c in text.lower() if c.isalnum())


@pytest.mark.parametrize("q", reference)
def test_answer_matches_reference(q):
    assert normalize(answers[q]) == normalize(reference[q])
