import os
import time
import tiktoken
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.globals import set_llm_cache
from langchain_redis import RedisSemanticCache
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
MODEL_NAME = "gpt-4o-mini"
ENCODER = tiktoken.encoding_for_model(MODEL_NAME)
REDIS_URL = "redis://localhost:6379"


def count_tokens(text: str) -> int:
    return len(ENCODER.encode(text))

def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    # gpt-4o-mini pricing: $0.15/1M input, $0.60/1M output [VERIFY]
    input_cost = (input_tokens / 1_000_000) * 0.15
    output_cost = (output_tokens / 1_000_000) * 0.60
    return input_cost + output_cost


class TokenBudgetManager:
    def __init__(self, request_limit=4000, daily_limit=50000):
        self.request_limit = request_limit
        self.daily_limit = daily_limit
        self.usage = {}  # {"user_id:2025-02-23": total_tokens}

    def _daily_key(self, user_id: str) -> str:
        return f"{user_id}:{time.strftime('%Y-%m-%d')}"

    def check_budget(self, user_id: str, input_tokens: int,
                     estimated_output: int = 500) -> dict:
        total_est = input_tokens + estimated_output
        
        if total_est > self.request_limit:
            return {"allowed": False, "reason": "request_limit_exceeded"}
        
        daily_used = self.usage.get(self._daily_key(user_id), 0)
        
        if daily_used + total_est > self.daily_limit:
            return {"allowed": False, "reason": "daily_limit_exceeded"}
        
        return {"allowed": True, "remaining": self.daily_limit - daily_used}
    
    def spend(self, user_id: str, tokens_used: int) -> dict:
        key = self._daily_key(user_id)
        self.usage[key] = self.usage.get(key, 0) + tokens_used
        
        return {
            "tokens_used": tokens_used,
            "daily_total": self.usage[key],
            "daily_remaining": self.daily_limit - self.usage[key],
            "est_cost": estimate_cost(tokens_used // 2, tokens_used // 2),
        }
        
        
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
semantic_cache = RedisSemanticCache(
    redis_url=REDIS_URL,
    embeddings=embeddings,
    distance_threshold=0.2,  # cosine distance: lower = stricter matching
    ttl=3600,  # cache entries expire after 1 hour
)
set_llm_cache(semantic_cache)

llm = ChatOpenAI(model=MODEL_NAME, temperature=0)
budget = TokenBudgetManager(request_limit=4000, daily_limit=50000)


def query(user_id: str, prompt: str) -> dict:
    input_tokens = count_tokens(prompt)
    check = budget.check_budget(user_id, input_tokens)
    
    if not check["allowed"]:
        return {"error": check["reason"], "response": None}
    
    start = time.time()
    response = llm.invoke(prompt)
    elapsed = time.time() - start
    cache_hit = elapsed < 1.0  # embedding ~0.2-0.5s vs LLM ~2-10s
    output_tokens = count_tokens(response.content)
    
    if cache_hit:
        daily = budget.usage.get(budget._daily_key(user_id), 0)
        usage = {"tokens_used": 0, "daily_total": daily,
                 "daily_remaining": budget.daily_limit - daily, "est_cost": 0.0}
    else:
        usage = budget.spend(user_id, input_tokens + output_tokens)
        
    return {"response": response.content, "input_tokens": input_tokens,
            "output_tokens": output_tokens, "cache_hit": cache_hit,
            "latency": round(elapsed, 2), **usage}
    

if __name__ == "__main__":
    queries = [
        "What are the main benefits of microservices?",
        "What are the main benefits of microservices?",
        "Tell me the key advantages of a microservice architecture",
    ]

    for i, q in enumerate(queries):
        print(f"\n--- Query {i+1}: '{q[:50]}...' ---")
        result = query("user_123", q)
        if result.get("error"):
            print(f"  BLOCKED: {result['error']}")
        else:
            print(f"  Cache hit:  {result['cache_hit']} ({result['latency']}s)")
            print(f"  Tokens:     {result['input_tokens']}+{result['output_tokens']}")
            print(f"  Daily used: {result['daily_total']}/{budget.daily_limit}")
            
    # Budget enforcement test
    print("\n--- Budget Enforcement Test ---")
    tight_budget = TokenBudgetManager(request_limit=4000, daily_limit=1000)

    for i in range(5):
        input_t = count_tokens("Explain quantum computing")
        check = tight_budget.check_budget("test_user", input_t,
                                          estimated_output=350)
        if check["allowed"]:
            tight_budget.spend("test_user", 400)  # simulate usage
            print(f"  Request {i+1}: ALLOWED (remaining: {check['remaining']})")
        else:
            print(f"  Request {i+1}: BLOCKED — {check['reason']}")