import httpx
from faults import inject

FIXTURE, TIMEOUT = "http://127.0.0.1:8100", 5.0
STOCK = {"A-1001": 12, "B-2002": 0, "C-3003": 4}


async def check_stock(sku: str) -> dict:
    return {"sku": sku, "units": STOCK.get(sku, 0)}


async def shipping_days(sku: str) -> dict:
    return {"sku": sku, "days": 2 if STOCK.get(sku, 0) else 10}


@inject
async def lookup_price(sku: str, _delay: float = 0.0) -> dict:
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as c:
            r = await c.get(f"{FIXTURE}/price/{sku}", params={"delay": _delay})
            return r.json()
    except httpx.TimeoutException:
        return {"sku": sku, "price": None, "currency": "USD"}


def schema(name: str, desc: str) -> dict:
    return {
        "name": name,
        "description": desc,
        "input_schema": {
            "type": "object",
            "properties": {"sku": {"type": "string"}},
            "required": ["sku"],
        },
    }


TOOLS = {
    "check_stock": check_stock,
    "shipping_days": shipping_days,
    "lookup_price": lookup_price,
}

TOOL_SCHEMAS = [
    schema("check_stock", "Units in stock for a SKU."),
    schema("shipping_days", "Shipping time in days for a SKU."),
    schema("lookup_price", "Current price for a SKU."),
]
