import asyncio
import dataclasses
import sys
from functools import reduce
from typing import (
    Any,
    AsyncGenerator,
    Awaitable,
    Callable,
    Generator,
    List,
    Protocol,
    Type,
    runtime_checkable,
)

import numpy as np
from koil import unkoil, unkoil_gen
from koil.composition.base import KoiledModel

from akuire.acquisition import Acquisition, AcquisitionResult
from akuire.compilers.default import compile_events
from akuire.config import SystemConfig
from akuire.events import (
    DataEvent,
    ImageDataEvent,
    ManagerEvent,
    MoveEvent,
    ZChangeEvent,
)
from akuire.vars import set_current_engine

Hook = Callable[[DataEvent], Awaitable[None]]


class AcquisitionEngine(KoiledModel):
    """Acquisition engine that orchestrates the acquisition of data from multiple devices.

    The AcquisitionEngine is the main entry point for orchestrating the acquisition of data from multiple devices.
    It is responsible for compiling the events that need to be executed, and for executing them in the correct order,
    ensuring that the data is collected in the correct order.

    """

    system_config: SystemConfig
    compiler: Callable[[Acquisition, SystemConfig], List[ManagerEvent]] = compile_events
    _lock: asyncio.Lock | None = None
    check_event_type: bool = True

    def acquire_sync(self, x: Acquisition) -> AcquisitionResult:
        return unkoil(self.acquire, x)

    def acquire_stream_sync(self, x: Acquisition) -> Generator[DataEvent, None, None]:
        for i in unkoil_gen(self.acquire_stream, x):
            yield i

    async def acquire_stream(self, x: Acquisition) -> AsyncGenerator[DataEvent, None]:

        events_queue = self.compiler(x, self.system_config)
        for paired_events in events_queue:
            for paired_event in paired_events:
                manager = self.system_config.get_manager(paired_event.manager)

                async for event in manager.compute_event(paired_event.event):
                    if self.check_event_type and not isinstance(event, DataEvent):
                        raise TypeError(
                            f"Event {event} is not a DataEvent. Only DataEvents are allowed in the stream. Inspect the event and manager that produced it. {paired_event.manager} produced {event.__class__}"
                        )
                    yield event

    async def acquire(
        self, x: Acquisition, hooks: list[Hook] | None = None
    ) -> AcquisitionResult:

        collected_events = []
        hooks = hooks or []

        async for event in self.acquire_stream(x):
            collected_events.append(event)
            for hook in hooks:
                await hook(event)

        return AcquisitionResult(collected_events)

    async def __aenter__(self) -> "AcquisitionEngine":
        self._lock = asyncio.Lock()
        set_current_engine(self)

        for manager in self.system_config.managers:
            await manager.__aenter__()

        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self._lock = None
        set_current_engine(None)

        for manager in self.system_config.managers:
            await manager.__aexit__(exc_type, exc_value, traceback)
        pass

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True
