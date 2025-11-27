from behavior import BehaviorSpec, CognitiveBoundaries, ConstraintPrompt, OutputGuard
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)


client = OpenAI()


class BehavioralAgent:
    def __init__(self, spec: BehaviorSpec):
        self.spec = spec
        self.boundaries = CognitiveBoundaries(spec.reasoning_depth)

    def build_prompt(self, user_input: str) -> str:
        shaped = ConstraintPrompt.apply(user_input, self.spec)
        shaped = self.boundaries.apply(shaped)

        system_header = (
            "You are an AI agent wrapped in a behavioral shell.\n"
            "Follow the constraints strictly.\n"
            "Respond ONLY with valid JSON that matches the schema.\n"
        )

        schema_hint = (
            "Expected JSON schema:\n"
            '{\n'
            '  "reasoning": "short explanation of your thinking",\n'
            '  "answer": "final answer that respects your constraints"\n'
            '}\n'
            "IMPORTANT: The 'answer' must be a SINGLE plain-text string. "
            "Do NOT return nested objects or lists.\n"

        )

        return system_header + "\n" + schema_hint + "\n" + shaped

    def run(self, user_input: str) -> dict:
        prompt = self.build_prompt(user_input)

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a careful, JSON-only reasoning engine."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )

        raw_content = completion.choices[0].message.content

        try:
            validated = OutputGuard.validate_json(raw_content)
            return validated.model_dump()
        except Exception as e:
            return {
                "error": "Invalid model output",
                "raw": raw_content,
                "details": str(e),
            }


def demo():
    spec = BehaviorSpec(
        name="RequirementAnalyst",
        goal="Extract only engineering requirements and missing information.",
        allowed_operations=[
            "Summarize constraints",
            "List explicit requirements",
            "Identify missing information",
        ],
        prohibited_operations=[
            "Write code",
            "Propose architectures",
            "Make business decisions",
        ],
        reasoning_depth=3,
    )

    agent = BehavioralAgent(spec)

    print("Behavioral shell demo. Paste a problem statement, then press Enter.")
    user_input = input("\nProblem statement: ")

    print("\n--- Shell prompt sent to the model (truncated) ---")
    preview = agent.build_prompt(user_input)
    print(preview[:600] + "...\n")

    result = agent.run(user_input)

    print("--- Validated agent output ---")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    demo()
