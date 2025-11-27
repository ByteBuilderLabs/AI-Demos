import requests
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

client = OpenAI()

def web_search(query: str) -> dict:
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json",
    }
    payload = {"q": query}

    res = requests.post(url, json=payload, headers=headers)
    res.raise_for_status()
    data = res.json()

    organic = data.get("organic", [])
    if not organic:
        return {"query": query, "result": "No search results found."}

    first = organic[0]

    return {
        "query": query,
        "title": first.get("title", ""),
        "link": first.get("link", ""),
        "result": first.get("snippet", "No snippet available.")
    }
    
    
def fact_check(text: str) -> dict:
    prompt = (
        "You are a fact-checking assistant. Verify the accuracy of the text "
        "and return a short, reliable summary.\n\n"
        f"Text to verify:\n{text}"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Return only verified facts."},
            {"role": "user", "content": prompt},
        ],
    )

    summary = response.choices[0].message.content
    return {"verified_summary": summary}