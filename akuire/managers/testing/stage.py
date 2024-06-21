import asyncio
import dataclasses
from typing import AsyncGenerator

import numpy as np

from akuire.events import (
    DataEvent,
    HasMovedEvent,
    ManagerEvent,
    MoveEvent,
    MoveXEvent,
    MoveYEvent,
)
from akuire.managers.base import BaseManager


@dataclasses.dataclass
class VirtualStageManager(BaseManager):

    async def compute_event(
        self, event: MoveXEvent | MoveYEvent | MoveEvent
    ) -> AsyncGenerator[DataEvent, None]:
        print("Moving stage")

        yield HasMovedEvent(x=event.x, device=self.device)

    def challenge(self, event: ManagerEvent) -> bool:
        return isinstance(event, MoveEvent)
        return isinstance(event, MoveEvent)
