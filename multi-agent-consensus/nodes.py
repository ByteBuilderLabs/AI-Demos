from typing import Optional
from langchain_anthropic import ChatAnthropic
from schemas import Verdict, DebateState

llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)
structured_llm = llm.with_structured_output(Verdict)


def run_agent(role: str, question: str, peer: Optional[Verdict]) -> Verdict:
    peer_text = (
        f"Your peer answered: {peer.answer}\nTheir evidence: {peer.evidence}"
        if peer
        else "No peer answer yet. Answer independently."
    )
    prompt = (
        f"You are {role}.\nQuestion: {question}\n{peer_text}\n"
        "If your peer is right, agree. If not, attack their reasoning and cite evidence."
    )
    return structured_llm.invoke(prompt)


def _line(rnd: int, name: str, v: Verdict) -> str:
    return (
        f"[Round {rnd}] {name}: {v.answer}\n"
        f"    agrees: {v.agrees_with_peer}  |  why: {v.evidence}"
    )


def propose(state: DebateState) -> dict:
    q = state["question"]
    a = run_agent("Agent A, a careful analyst", q, None)
    b = run_agent("Agent B, a skeptical fact-checker", q, None)
    log = [_line(1, "A", a), _line(1, "B", b)]
    return {"verdict_a": a, "verdict_b": b, "round": 1, "transcript": log}


def cross_examine(state: DebateState) -> dict:
    q, r = state["question"], state["round"] + 1
    a = run_agent("Agent A", q, state["verdict_b"])
    b = run_agent("Agent B", q, state["verdict_a"])
    log = [_line(r, "A", a), _line(r, "B", b)]
    return {"verdict_a": a, "verdict_b": b, "round": r, "transcript": log}


MAX_ROUNDS = 3


def route(state: DebateState) -> str:
    a, b = state["verdict_a"], state["verdict_b"]
    agree = a.answer.strip().lower() == b.answer.strip().lower()
    if agree or (a.agrees_with_peer and b.agrees_with_peer):
        return "finalize"
    return "judge" if state["round"] >= MAX_ROUNDS else "cross_examine"


def finalize(state: DebateState) -> dict:
    return {"final_answer": state["verdict_a"].answer}


def judge(state: DebateState) -> dict:
    log = "\n".join(state["transcript"])
    pick = llm.invoke(f"Agents disagreed. Pick the best-supported answer:\n{log}")
    return {"final_answer": pick.content}
