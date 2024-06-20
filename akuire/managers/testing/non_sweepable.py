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
class NonSweepableCamera(Manager):
    exposition_time_is_sleep: bool = False

    async def compute_event(
        self, event: AcquireFrameEvent | ZChangeEvent
    ) -> AsyncGenerator[DataEvent, None]:

        if isinstance(event, AcquireFrameEvent):
            print("Acquiring frame")
            if self.exposition_time_is_sleep:
                await asyncio.sleep(event.exposition_time)
            yield ImageDataEvent(data=np.random.rand(1, 512, 512, 1))

        yield ImageDataEvent(data=np.random.rand(1, 512, 512, 1))

    def challenge(self, event: ManagerEvent) -> bool:
        return isinstance(event, AcquireFrameEvent)
