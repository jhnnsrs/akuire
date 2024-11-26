import asyncio

from akuire.events.data_event import FinishedEvent
from akuire.events.manager_event import DelayEvent
from akuire.managers.base import BaseManager, Manager


class DelayManager(BaseManager):
    """A manager that computes a delay event on the software level"""

    async def compute_event(self, event: DelayEvent):
        assert event.timeout is not None, "DelayEvent must have a timeout"
        await asyncio.sleep(event.timeout / 1000)
        yield FinishedEvent(device=self.device)
