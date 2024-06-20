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
class ZStageManager(Manager):

    async def compute_event(
        self, event: ZChangeEvent
    ) -> AsyncGenerator[DataEvent, None]:
        print("Changed Z")
        yield ZChangeEvent(z=event.z)

    def challenge(self, event: ManagerEvent) -> bool:
        return isinstance(event, ZChangeEvent)
