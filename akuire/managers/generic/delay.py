import asyncio
import dataclasses
from typing import AsyncGenerator

import numpy as np

from akuire.events import (
    AcquireFrameEvent,
    AcquireZStackEvent,
    DataEvent,
    DelayEvent,
    HasMovedEvent,
    ImageDataEvent,
    ManagerEvent,
    ZChangeEvent,
)
from akuire.managers.base import Manager


@dataclasses.dataclass
class DelayManager(Manager):
    def __init__(self, delay):
        self.delay = delay

    def __enter__(self):
        self.delay.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.delay.stop()

    async def compute_event(self, event: DelayEvent) -> AsyncGenerator[DataEvent, None]:

        await asyncio.sleep(self.delay.timeout)
        yield HasMovedEvent(z=event.z, device=self.device)

    def challenge(self, event: ManagerEvent) -> bool:
        if isinstance(event, DelayEvent):
            return True
