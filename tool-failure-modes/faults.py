import functools, os
from contextvars import ContextVar

_first_call = ContextVar("first_call", default=True)
BAD_JSON = '{"sku": "A-1001", "price": }'


def _transient_503() -> bool:
    if _first_call.get():
        _first_call.set(False)
        return True
    return False


def inject(fn):
    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        mode = os.getenv("FAULT_MODE", "none")
        if mode == "raise" and _transient_503():
            raise RuntimeError("vendor 503: price service unavailable")
        if mode == "malformed":
            return BAD_JSON
        if mode == "empty":
            return {"sku": kwargs.get("sku"), "results": []}
        if mode == "slow":
            kwargs["_delay"] = 8.0
        return await fn(*args, **kwargs)

    return wrapper
