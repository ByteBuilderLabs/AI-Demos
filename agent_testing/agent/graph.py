from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()


@tool
def get_weather(city: str) -> str:
    """Look up the current weather for a given city name."""
    mock_data = {
        "london": "15°C, cloudy",
        "tokyo": "22°C, sunny",
        "new york": "18°C, partly cloudy",
    }
    return mock_data.get(city.lower(), f"No data for {city}")


@tool
def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """Convert a numeric value between measurement units."""
    conversions = {
        ("km", "miles"): lambda v: v * 0.621371,
        ("kg", "lbs"): lambda v: v * 2.20462,
        ("celsius", "fahrenheit"): lambda v: (v * 9 / 5) + 32,
    }
    fn = conversions.get((from_unit.lower(), to_unit.lower()))
    if fn is None:
        return f"Cannot convert {from_unit} to {to_unit}"
    result = fn(value)
    return f"{value} {from_unit} = {result:.2f} {to_unit}"


tools = [get_weather, convert_units]
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
agent = create_agent(model, tools)


def run_agent(inputs: dict) -> dict:
    result = agent.invoke({"messages": [HumanMessage(content=inputs["input"])]})
    final = result["messages"][-1].content
    return {
        "output": final,
        "messages": result["messages"],
    }
