import asyncio
import dataclasses
from typing import AsyncGenerator

import numpy as np

from akuire.events import (
    AcquireFrameEvent,
    AcquireZStackEvent,
    DataEvent,
    HasMovedEvent,
    ImageDataEvent,
    ManagerEvent,
    ZChangeEvent,
)
from akuire.managers.base import BaseManager


@dataclasses.dataclass
class SweepableCamera(BaseManager):

    async def compute_event(
        self, event: AcquireFrameEvent | ZChangeEvent | AcquireZStackEvent
    ) -> AsyncGenerator[DataEvent, None]:

        if isinstance(event, AcquireFrameEvent):
            print("Acquiring frame")
            await asyncio.sleep(event.exposure_time)
            yield ImageDataEvent(
                data=np.random.rand(1, 1, 1, 512, 512, 1), device=self.device
            )

        if isinstance(event, ZChangeEvent):
            print("Changing z")
            yield HasMovedEvent(z=event.z, device=self.device)

        if isinstance(event, AcquireZStackEvent):
            print("Streaming Z-Stack")
            for i in range(event.z_steps):
                await asyncio.sleep(event.item_exposure_time)
                yield ImageDataEvent(
                    data=np.random.rand(1, 1, 1, 512, 512), device=self.device
                )

    def challenge(self, event: ManagerEvent) -> bool:
        if isinstance(event, AcquireFrameEvent):
            return True
        if isinstance(event, ZChangeEvent):
            return True
        if isinstance(event, AcquireZStackEvent):
            return True
        return False
