import json
from dotenv import load_dotenv
from openai import OpenAI
from tools import web_search, fact_check

load_dotenv(override=True)
client = OpenAI()


tools = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Fetch live information from the web.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fact_check",
            "description": "Verify factual accuracy of text.",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        },
    },
]


def run_agent(user_input: str) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You MUST call the web_search tool for ANY request involving external, "
                "recent, live, current, up-to-date, or real-world information. ..."
            )
        },
        {"role": "user", "content": user_input},
    ]
    
    
    print("\n=== USER INPUT ===")
    print(user_input)
    print("==================\n")

    step = 1

    while True:
        print(f"[STEP {step}] Calling model...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
        )
        
        msg = response.choices[0].message
        step += 1

        if not msg.tool_calls:
            print("\n=== FINAL MODEL RESPONSE ===")
            print(msg.content)
            print("============================\n")
            return msg.content


        print(f"[MODEL] Requested {len(msg.tool_calls)} tool call(s):")

        for tool_call in msg.tool_calls:
            tool_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            print(f"→ Tool request: {tool_name}({args})")

            if tool_name == "web_search":
                result = web_search(**args)
            elif tool_name == "fact_check":
                result = fact_check(**args)
            else:
                result = {"error": f"Unsupported tool: {tool_name}"}


            messages.append(msg)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            })

if __name__ == "__main__":
    question = "Search for the latest quantum computing news and verify it."
    print(run_agent(question))
