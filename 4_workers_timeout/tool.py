import time, httpx
from collections import defaultdict

VENDOR = "http://127.0.0.1:9000"
CLIENT = httpx.Client(timeout=httpx.Timeout(2.0, connect=1.0))
DEADLINE = 3.0


class Breaker:
    fails, cooldown = 3, 15
    count, opened = 0, 0.0

    def is_open(self):
        cold = time.monotonic() - self.opened
        return self.count >= self.fails and cold < self.cooldown

    def record(self, failed):
        self.count = self.count + 1 if failed else 0
        self.opened = time.monotonic()


BREAKERS = defaultdict(Breaker)


def call_vendor(path: str = "/ok"):
    breaker = BREAKERS[path]
    if breaker.is_open():
        raise RuntimeError("circuit open")
    deadline = time.monotonic() + DEADLINE
    while (left := deadline - time.monotonic()) > 0:
        try:
            r = CLIENT.get(f"{VENDOR}{path}", timeout=min(2.0, left))
            breaker.record(False)
            return r.json()
        except httpx.TimeoutException:
            pass
    breaker.record(True)
    raise RuntimeError("vendor timeout")
