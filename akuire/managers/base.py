from typing import AsyncContextManager, AsyncGenerator, Protocol, runtime_checkable

from akuire.events.data_event import DataEvent
from akuire.events.manager_event import ManagerEvent


@runtime_checkable
class Manager(Protocol):
    device: str = "default"

    async def compute_event(
        self, event: ManagerEvent
    ) -> AsyncGenerator[DataEvent, None]: ...

    def challenge(self, event: ManagerEvent) -> bool:
        """Check if the manager can handle the event

        The challenge method is used to check if the manager can handle a specific event. This method should return True
        if the manager can handle the event and False otherwise.

        The AcquistionEngine will use this method to determine if the manager can handle the event. If the manager can
        handle the event, the compute_event method will be called to execute the event.


        """
        ...
