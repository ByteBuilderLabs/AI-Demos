import asyncio
from uuid import uuid4
import httpx
from a2a.client import ClientFactory, ClientConfig
from a2a.types import Message, Part, TextPart

async def main():
    client = await ClientFactory.connect(
        "http://localhost:9999",
        client_config=ClientConfig(
            httpx_client=httpx.AsyncClient(timeout=60.0)
        ),
    )

    message = Message(
        role="user",
        parts=[Part(root=TextPart(text="What is the A2A protocol?"))],
        messageId=uuid4().hex,
    )

    async for response in client.send_message(message):
        print(response.model_dump(mode="json", exclude_none=True))

asyncio.run(main())