import json, os, sys
import anthropic
from tools import TOOLS, charge_customer

client = anthropic.Anthropic()


def agent(run_id, arm, msgs):
    while True:
        if msgs[-1]["role"] == "user":
            resp = client.messages.create(
                model="claude-haiku-5-5", max_tokens=1024, tools=TOOLS, messages=msgs
            )
            msgs.append(
                {
                    "role": "assistant",
                    "content": [b.model_dump(exclude_none=True) for b in resp.content],
                }
            )
        calls = [b for b in msgs[-1]["content"] if b["type"] == "tool_use"]
        if not calls:
            return "".join(b.get("text", "") for b in msgs[-1]["content"])
        msgs.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": c["id"],
                        "content": json.dumps(
                            charge_customer(run_id, arm, **c["input"])
                        ),
                    }
                    for c in calls
                ],
            }
        )


TASK = "Charge customer cus_017 4900 cents for order ORD-1042, then confirm in one sentence."


class Checkpoint(list):
    def __init__(self, run_id):
        self.path = os.path.join("checkpoints", f"{run_id}.json")
        super().__init__(
            json.load(open(self.path))
            if os.path.exists(self.path)
            else [{"role": "user", "content": TASK}]
        )

    def append(self, msg):
        super().append(msg)
        with open(self.path + ".tmp", "w") as f:
            json.dump(self, f)
        os.replace(self.path + ".tmp", self.path)


if __name__ == "__main__":
    print(agent(sys.argv[1], sys.argv[2], Checkpoint(sys.argv[1])))
