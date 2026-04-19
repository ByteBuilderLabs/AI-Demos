from dotenv import load_dotenv
from langsmith import Client

load_dotenv()
client = Client()
dataset_name = "agent-golden-set"

examples = [
    {
        "inputs": {"question": "What's the weather in Tokyo?"},
        "outputs": {"answer": "72F and sunny", "expected_tool": "get_weather"},
    },
    {
        "inputs": {"question": "What's the price of AAPL?"},
        "outputs": {"answer": "$150.42", "expected_tool": "get_stock_price"},
    },
    {
        "inputs": {"question": "Weather in Paris please"},
        "outputs": {"answer": "72F and sunny", "expected_tool": "get_weather"},
    },
]

dataset = client.create_dataset(dataset_name)
client.create_examples(dataset_id=dataset.id, examples=examples)
print(f"Dataset '{dataset_name}' created with {len(examples)} examples.")
