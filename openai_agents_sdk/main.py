import asyncio
import os

from dotenv import load_dotenv
from agents import (
    Agent,
    Runner,
    InputGuardrail,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
)

from schemas import WriterResult, TopicCheck

load_dotenv()

writer_agent = Agent(
    name="Writer",
    instructions="You receive research findings and write a concise, professional summary. Include all key points.",
    output_type=WriterResult,
)


topic_checker = Agent(
    name="Topic Checker",
    instructions="Determine if the input is a legitimate research topic."
    + "Return is_valid_topic=True for real research queries, False for jokes, casual chat, or off-topic requests.",
    output_type=TopicCheck,
)


async def check_topic(ctx, agent, input_text):
    result = await Runner.run(topic_checker, input_text, context=ctx.context)
    return GuardrailFunctionOutput(
        tripwire_triggered=not result.final_output.is_valid_topic,
        output_info={"reason": result.final_output.reasoning},
    )


research_agent = Agent(
    name="Researcher",
    instructions="You research the given topic thoroughly. Gather key facts and findings,"
    + "then hand off to the Writer agent to create a summary.",
    handoffs=[writer_agent],
    input_guardrails=[InputGuardrail(guardrail_function=check_topic)],
)


async def main():
    try:
        result = await Runner.run(
            research_agent,
            "Tell me a joke",
        )
        print(f"Final output: {result.final_output}")
        print(f"Last agent: {result.last_agent.name}")
    except InputGuardrailTripwireTriggered:
        print("Guardrail tripped: not a valid research topic.")


if __name__ == "__main__":
    asyncio.run(main())
