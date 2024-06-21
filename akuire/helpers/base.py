from typing import AsyncGenerator

from akuire.acquisition import Acquisition, AcquisitionResult
from akuire.engine import AcquisitionEngine
from akuire.events import AcquireFrameEvent, AcquireZStackEvent, DataEvent
from akuire.vars import get_current_engine


async def one_shot_snap(
    engine: AcquisitionEngine = None,
    **kwargs,
) -> AsyncGenerator[AcquireFrameEvent, None]:

    engine = engine or get_current_engine()

    async for i in engine.acquire_stream(
        Acquisition(
            events=[
                AcquireFrameEvent(
                    **kwargs,
                )
            ]
        )
    ):
        yield i


async def acquire_z_stack(
    engine: AcquisitionEngine = None,
    z_steps: int = 10,
    **kwargs,
) -> AsyncGenerator[DataEvent, None]:

    engine = engine or get_current_engine()

    async for i in engine.acquire_stream(
        Acquisition(
            events=[
                AcquireZStackEvent(
                    z_steps=z_steps,
                    **kwargs,
                )
            ]
        )
    ):
        yield i
