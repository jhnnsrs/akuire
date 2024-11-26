import dataclasses
from typing import (
    AsyncContextManager,
    AsyncGenerator,
    Protocol,
    get_args,
    runtime_checkable,
)

from akuire.events.data_event import DataEvent
from akuire.events.manager_event import ManagerEvent
import inspect


@runtime_checkable
class Manager(Protocol):
    def get_device_name(self) -> str: ...

    async def __aenter__(self) -> AsyncContextManager["Manager"]: ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...

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


@dataclasses.dataclass
class BaseManager:
    device: str = "default"
    __typed_challengers = None

    async def __aenter__(self) -> AsyncContextManager["BaseManager"]:
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    def get_device_name(self) -> str:
        return self.device

    async def compute_event(
        self, event: ManagerEvent
    ) -> AsyncGenerator[DataEvent, None]:
        raise NotImplementedError(
            "compute_event method must be implemented in the subclass"
        )

    def challenge(self, event: ManagerEvent) -> bool:
        """Check if the manager can handle the event

        The challenge method is used to check if the manager can handle a specific event. This method should return True
        if the manager can handle the event and False otherwise.

        The AcquistionEngine will use this method to determine if the manager can handle the event. If the manager can
        handle the event, the compute_event method will be called to execute the event.


        """
        if self.__typed_challengers is None:
            for key, value in inspect.signature(self.compute_event).parameters.items():
                annotation = value.annotation
                try:
                    if issubclass(annotation, ManagerEvent):
                        self.__typed_challengers = [annotation]
                except TypeError:
                    union_types = []
                    for i in get_args(annotation):
                        if issubclass(i, ManagerEvent):
                            union_types.append(i)
                        else:
                            raise TypeError(
                                f"Annotation {i} is not a subclass of ManagerEvent nor a union of ManagerEvent subclasses"
                            )

                    self.__typed_challengers = union_types

        if event.__class__ in self.__typed_challengers:
            return True

        return False
