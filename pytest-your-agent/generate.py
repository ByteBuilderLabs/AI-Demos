import json
from openai import OpenAI
from dataset import QA

client = OpenAI()
SYS = "Answer with only the fact. No sentences, no articles, no parentheses."
answers = []

for item in QA:
    msgs = [{"role": "system", "content": SYS}, {"role": "user", "content": item["q"]}]
    resp = client.chat.completions.create(model="gpt-4o-mini", messages=msgs)
    answers.append(
        {"q": item["q"], "model_answer": resp.choices[0].message.content.strip()}
    )

json.dump(answers, open("answers.json", "w"), indent=2)
print(f"Saved {len(answers)} answers")
