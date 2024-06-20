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
from akuire.managers.base import Manager


@dataclasses.dataclass
class SweepableManager(Manager):

    async def compute_event(
        self, event: AcquireFrameEvent | ZChangeEvent | AcquireZStackEvent
    ) -> AsyncGenerator[DataEvent, None]:

        if isinstance(event, AcquireFrameEvent):
            print("Acquiring frame")
            yield ImageDataEvent(data=np.random.rand(1, 1, 1, 512, 512, 1))

        if isinstance(event, ZChangeEvent):
            print("Changing z")
            yield ZChangeEvent(z=event.z)

        if isinstance(event, AcquireZStackEvent):
            print("Streaming Z-Stack")
            yield ImageDataEvent(data=np.random.rand(1, 1, event.z_steps, 512, 512))

    def challenge(self, event: ManagerEvent) -> bool:
        if isinstance(event, AcquireFrameEvent):
            return True
        if isinstance(event, ZChangeEvent):
            return True
        if isinstance(event, AcquireZStackEvent):
            return True
        return False
