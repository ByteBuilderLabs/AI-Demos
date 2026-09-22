import time
import httpx
from tenacity import retry, stop_after_attempt, wait_random_exponential
from agent import fetch


class RetryBudget:
    def __init__(self, ratio=0.1, floor=3):
        self.ratio, self.floor, self.requests, self.retries = ratio, floor, 0, 0

    def __call__(self, state) -> bool:  # tenacity calls this after every failed attempt
        is_timeout = isinstance(state.outcome.exception(), httpx.TimeoutException)
        if not is_timeout or self.retries >= self.floor + self.ratio * self.requests:
            return False
        self.retries += 1
        return True


class CircuitOpen(Exception):
    pass


class CircuitBreaker:
    def __init__(self, threshold=5, cooldown=5.0):
        self.threshold, self.cooldown = threshold, cooldown
        self.failures, self.open_until = 0, 0.0

    def check(self):
        if time.monotonic() < self.open_until:
            raise CircuitOpen("Dependency overloaded. Do not call this tool again.")

    def record(self, ok: bool):
        self.failures = 0 if ok else self.failures + 1
        if self.failures >= self.threshold:
            self.open_until = time.monotonic() + self.cooldown


budget = RetryBudget(ratio=0.1)
breaker = CircuitBreaker(threshold=5, cooldown=5.0)


@retry(
    stop=stop_after_attempt(3),
    retry=budget,
    wait=wait_random_exponential(multiplier=1, max=10),
)
async def guarded_lookup(order_id: str) -> str:
    breaker.check()
    budget.requests += 1
    try:
        result = await fetch(order_id)
    except httpx.HTTPError:
        breaker.record(ok=False)
        raise
    breaker.record(ok=True)
    return result
