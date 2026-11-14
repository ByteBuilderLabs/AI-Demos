import hashlib, json
from pathlib import Path
from openai import OpenAI

MODEL, client = "gpt-4.1-mini", OpenAI(max_retries=10)  # frozen; retries ride out 429s
CACHE, tokens_used = (
    Path("cache.json"),
    [],
)  # tokens_used: only calls we actually paid for
cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}


def complete(**request):  # temperature 0: same request, same answer, so cache it
    key = hashlib.sha256(
        json.dumps([MODEL, request], sort_keys=True).encode()
    ).hexdigest()
    if key not in cache:
        out = client.chat.completions.create(model=MODEL, temperature=0, **request)
        cache[key] = out.choices[0].message.content
        tokens_used.append(out.usage.total_tokens)
    return cache[key]


def ask(history, user_msg, build_payload, must_keep=()):
    history.append({"role": "user", "content": user_msg})
    payload = build_payload(history, must_keep)
    reply = complete(
        messages=payload, max_completion_tokens=20
    )  # answers are one short ID
    history.append({"role": "assistant", "content": reply})
    return reply, payload
