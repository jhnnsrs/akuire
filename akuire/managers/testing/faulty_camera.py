import asyncio
import dataclasses
from typing import AsyncGenerator

import numpy as np

from akuire.events import (
    AcquireFrameEvent,
    AcquireZStackEvent,
    DataEvent,
    ImageDataEvent,
    ManagerEvent,
    ZChangeEvent,
)
from akuire.managers.base import BaseManager

from .errors import TestableError


class FaultyCameraError(TestableError):
    pass


@dataclasses.dataclass
class FaultyCamera(BaseManager):
    __lock = asyncio.Lock()
    __queue = asyncio.Queue()

    async def compute_event(
        self, event: AcquireFrameEvent | ZChangeEvent
    ) -> AsyncGenerator[DataEvent, None]:

        if isinstance(event, AcquireFrameEvent):
            print("Acquiring frame")
            async with self.__lock:
                raise FaultyCameraError("Camera is faulty")

        # // Just to make python understand that this is a generator
        yield ImageDataEvent(data=np.random.rand(1, 512, 512, 1))

    def challenge(self, event: ManagerEvent) -> bool:
        return isinstance(event, AcquireFrameEvent)

    async def __aenter__(self) -> "FaultyCamera":
        self.__lock = asyncio.Lock()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self.__lock = None
        return None
