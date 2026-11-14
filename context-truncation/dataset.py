import random

KINDS = [
    ("order ID", "ORD"),
    ("locker code", "LCK"),
    ("flight number", "FLT"),
    ("invoice number", "INV"),
    ("staging port", "PRT"),
    ("parking spot", "PKG"),
]
seed_rng = random.Random(7)  # fixed seed: the same 20 questions every run
QUESTIONS = []
for i in range(20):
    kind, prefix = KINDS[i % len(KINDS)]
    answer = f"{prefix}-{seed_rng.randint(1000, 9999)}"
    QUESTIONS.append(
        {
            "id": i,
            "fact": f"By the way, my {kind} is {answer}.",
            "question": f"What is my {kind}? Reply with just the value.",
            "answer": answer,
        }
    )


def grade(q, reply):  # the oracle: did the exact planted value come back?
    return q["answer"].lower() in (reply or "").lower()


TOPICS = ["the deploy pipeline","the billing service","the Postgres migration","the on-call rota",]

LINES = ["Ticket {n} is still open for {t}.","Last sprint {t} took {n} seconds to run.",
         "Someone said {t} broke again around build {n}.","We should review {t} before release {n}.",]


def chatter(rng):  # one sentence of plausible noise, with a distractor number in it
    return rng.choice(LINES).format(t=rng.choice(TOPICS), n=rng.randint(100, 9999))


def make_conversation(n_turns, position, q, seed):
    rng = random.Random(q["id"] * 1000 + seed)  # same seed, same conversation
    at = {"early": 0, "middle": n_turns // 2, "late": n_turns - 1}[position]
    convo = []
    for i in range(n_turns):
        user = chatter(rng) + (" " + q["fact"] if i == at else "")
        convo += [
            {"role": "user", "content": user},
            {"role": "assistant", "content": chatter(rng)},
        ]
    return convo
