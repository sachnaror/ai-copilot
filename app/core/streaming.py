import asyncio
from collections.abc import AsyncGenerator


async def token_stream(text: str, delay_seconds: float = 0.02) -> AsyncGenerator[str, None]:
    for token in text.split():
        yield token + " "
        await asyncio.sleep(delay_seconds)
