import json
from openai import OpenAI

client = OpenAI()
answers = json.load(open("answers.json"))

PROMPT = """Question: {q}
Answer given: {a}
Is the answer correct? Reply with exactly PASS or FAIL."""


passed = 0
for item in answers:
    msg = [
        {"role": "user", "content": PROMPT.format(q=item["q"], a=item["model_answer"])}
    ]
    resp = client.chat.completions.create(model="gpt-4o-mini", messages=msg)
    if resp.choices[0].message.content.strip().upper().startswith("PASS"):
        passed += 1

print(f"{passed}/{len(answers)} passed")
