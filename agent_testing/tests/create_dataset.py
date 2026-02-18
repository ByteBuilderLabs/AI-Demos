from langsmith import Client
from dotenv import load_dotenv

load_dotenv()
client = Client()

dataset = client.create_dataset(
    "agent-regression-suite",
    description="Regression tests for weather/converter agent",
)

examples = [
    {
        "input": "What's the weather in London?",
        "expected": {
            "tool": "get_weather",
            "args": {"city": "london"},
            "answer_contains": "cloudy",
        },
    },
    {
        "input": "Convert 10 km to miles",
        "expected": {
            "tool": "convert_units",
            "args": {"value": 10, "from_unit": "km", "to_unit": "miles"},
            "answer_contains": "6.21",
        },
    },
    {
        "input": "What's the weather in Tokyo?",
        "expected": {
            "tool": "get_weather",
            "args": {"city": "tokyo"},
            "answer_contains": "sunny",
        },
    },
    {
        "input": "Convert 100 celsius to fahrenheit",
        "expected": {
            "tool": "convert_units",
            "args": {"value": 100},
            "answer_contains": "212",
        },
    },
]

for ex in examples:
    client.create_example(
        inputs={"input": ex["input"]},
        outputs={"expected": ex["expected"]},
        dataset_id=dataset.id,
    )

print(f"Created dataset with {len(examples)} examples.")