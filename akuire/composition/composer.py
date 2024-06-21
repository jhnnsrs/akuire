from typing import AsyncGenerator

from akuire.acquisition import AcquisitionResult


async def arun(generator: AsyncGenerator) -> AcquisitionResult:

    collected = []

    async for i in generator:
        collected.append(i)

    return AcquisitionResult(collected_events=collected)
