import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class AgentRequest(BaseModel):
    prompt: str
    user_id: str


class AgentResponse(BaseModel):
    content: str
    timestamp: datetime = datetime.now()
    model_used: str = "gpt-4-turbo"


class ByteBuilderAgent:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found")
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"

    def run(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior AI engineer. Be concise and code-focused.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content


app = FastAPI(title="ByteBuilder Agent Service")
agent = ByteBuilderAgent()

@app.post("/chat", response_model=AgentResponse)
async def handle_chat(request: AgentRequest):
    try:
        answer = agent.run(request.prompt)
        return AgentResponse(content=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)