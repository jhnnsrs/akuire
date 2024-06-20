from typing import AsyncContextManager, AsyncGenerator, Protocol, runtime_checkable

from akuire.events.data_event import DataEvent
from akuire.events.manager_event import ManagerEvent


@runtime_checkable
class Manager(Protocol):
    device: str = "default"

    async def compute_event(
        self, event: ManagerEvent
    ) -> AsyncGenerator[DataEvent, None]: ...

    def challenge(self, event: ManagerEvent) -> bool: ...
