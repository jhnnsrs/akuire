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
class ZStageManager(BaseManager):

    async def compute_event(
        self, event: ZChangeEvent
    ) -> AsyncGenerator[DataEvent, None]:
        print("Changed Z")
        yield HasMovedEvent(z=event.z, device=self.device)

    def challenge(self, event: ManagerEvent) -> bool:
        return isinstance(event, ZChangeEvent)
