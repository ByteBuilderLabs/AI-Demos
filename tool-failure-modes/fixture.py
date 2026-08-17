import asyncio
from fastapi import FastAPI

PRICES = {"A-1001": 249.00, "B-2002": 89.50, "C-3003": 1310.00}

app = FastAPI()


@app.get("/price/{sku}")
async def price(sku: str, delay: float = 0.0):
    await asyncio.sleep(delay)
    return {"sku": sku, "price": PRICES[sku], "currency": "USD"}
