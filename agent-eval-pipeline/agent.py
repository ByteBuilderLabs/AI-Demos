from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

load_dotenv()


@tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"The weather in {city} is 72F and sunny."


@tool
def get_stock_price(ticker: str) -> str:
    """Get current stock price for a ticker."""
    return f"{ticker} is trading at $150.42"


model = ChatOpenAI(model="gpt-4o-mini")
agent = create_agent(
    model=model,
    tools=[get_weather, get_stock_price],
)
