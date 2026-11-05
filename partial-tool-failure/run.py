import sys
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from agent import run_agent, SCHEMAS
from faults import inject
from oracle import grade, QUESTION


def run_arm(runs=300, soft=False, **contract):
    def one(i):
        tools, broken = inject(i, soft)
        answer = run_agent(QUESTION, tools, **contract)
        return {"broken": broken, "answer": answer, **grade(answer, broken)}

    with ThreadPoolExecutor(max_workers=8) as pool:
        return pd.DataFrame(list(pool.map(one, range(runs))))


def report(name, df):
    df = df.assign(
        silent=~df.flagged & ~df.mentioned,
        confident_wrong=~df.correct & ~df.flagged,
        stuck=df.answer.str.contains("ran out of turns"),
    )
    df.to_json(f"{name}.jsonl", orient="records", lines=True)
    print(df.drop(columns="answer").groupby("broken").mean().round(2))
    print(
        f"{name}: silent {df.silent.mean():.0%}, confidently wrong {df.confident_wrong.mean():.0%}"
    )


if __name__ == "__main__":
    arm, soft = sys.argv[1], "--soft" in sys.argv
    runs = 30 if "--quick" in sys.argv else 300
    settings = {}
    if arm == "contract":
        from contract import gate, SUBMIT

        settings = {"handle": gate, "schemas": SCHEMAS + [SUBMIT], "choice": "any"}
    report(arm + ("-soft" if soft else ""), run_arm(runs, soft, **settings))
