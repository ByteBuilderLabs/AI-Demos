import anyio
from fastapi import FastAPI

app = FastAPI()


@app.get("/hang")
async def hang():
    await anyio.sleep_forever()


@app.get("/ok")
async def ok():
    return {"status": "ok"}
