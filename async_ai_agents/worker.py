import os
from dotenv import load_dotenv
from celery import Celery
from openai import OpenAI

load_dotenv()

celery_app = Celery(
    "agent_tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0"
)

client = OpenAI()


@celery_app.task(name="run_research_agent")
def run_research_agent(prompt: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert research agent."},
            {"role": "user", "content": prompt},
        ],
    )

    return {
        "status": "success",
        "prompt": prompt,
        "result": response.choices[0].message.content,
    }
