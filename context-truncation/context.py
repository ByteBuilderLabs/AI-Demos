from langchain_core.messages import trim_messages, convert_to_openai_messages
from langchain_core.messages.utils import count_tokens_approximately
from agent import complete  # the summariser uses this later

CONTEXT_BUDGET = 800  # tokens: about 20 turns, so 30 and 50 turns overflow


def framework_payload(history, must_keep):
    # must_keep is ignored on purpose: the framework has no idea what matters
    kept = trim_messages(
        history,
        max_tokens=CONTEXT_BUDGET,
        strategy="last",
        include_system=True,
        token_counter=count_tokens_approximately,
        start_on="human",
    )
    return convert_to_openai_messages(kept)


ARMS = {"baseline": framework_payload}  # the sweep picks an arm by name


TURN_BUDGET = 8  # the last 8 exchanges stay word for word
SUMMARY_PROMPT = (
    'Return JSON {"facts": [...]} with only personal details the user gave about '
    "themselves, like their own IDs or codes. Skip tickets, builds and releases. Copy values exactly."
)


def summarised_payload(history, must_keep):
    system, turns = history[0], history[1:]
    cut = max(0, len(turns) - 2 * TURN_BUDGET - 1)  # question + last 8 exchanges
    if cut == 0:
        return history
    old = "\n".join(f'{m["role"]}: {m["content"]}' for m in turns[:cut])
    facts = complete(
        messages=[
            {"role": "system", "content": SUMMARY_PROMPT},
            {"role": "user", "content": old},
        ],
        response_format={"type": "json_object"},
        max_completion_tokens=150,
    )
    note = {
        "role": "system",
        "content": "Facts from earlier in this conversation: " + facts,
    }
    return [system, note] + turns[cut:]


class ContextLossError(AssertionError):
    pass


def guarded(build_payload):
    def build(history, must_keep):
        payload = build_payload(history, must_keep)
        seen = " ".join(m["content"] for m in payload)
        missing = [f for f in must_keep if f not in seen]
        if missing:
            raise ContextLossError(
                f"{missing} not in payload ({len(payload)} of {len(history)} msgs kept)"
            )
        return payload

    return build


ARMS.update(guarded=guarded(framework_payload), fixed=guarded(summarised_payload))
