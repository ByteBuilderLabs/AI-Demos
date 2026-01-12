import instructor
from pydantic import BaseModel, Field
from openai import OpenAI
from typing import Literal


# 1. Define the Decision Schema
class RouterDecision(BaseModel):
    """Classifies user intent to select the optimal model architecture."""

    target_engine: Literal["GPT-5.2-REASONING", "GEMINI-3-CONTEXT"]
    complexity_score: float = Field(..., description="0.0 (Simple) to 1.0 (Deep Logic)")
    reason: str


# 2. Layer 1: The Classifier (Sub-100ms Latency)
client = instructor.from_openai(OpenAI())


def get_optimal_route(user_prompt: str) -> RouterDecision:
    return client.chat.completions.create(
        model="llama-3.1-8b-instruct",  # Low-cost, high-speed router
        response_model=RouterDecision,
        messages=[
            {
                "role": "system",
                "content": "Route to GPT if deep logic is needed. "
                + "Route to Gemini for multi-file/long context.",
            },
            {"role": "user", "content": user_prompt},
        ],
    )
    

# 3. Execution Logic
def execute_task(prompt: str):
    decision = get_optimal_route(prompt)
    print(f"ByteBuilder Routing: {decision.target_engine} (Score: {decision.complexity_score})")
    
    if decision.target_engine == "GPT-5.2-REASONING":
        # Call GPT-5.2 with high reasoning effort
        pass 
    else:
        # Call Gemini-3 with native context window
        pass
