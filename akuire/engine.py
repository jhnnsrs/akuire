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
from koil import unkoil
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

    async def astart(self):
        pass

    def start(self):
        return unkoil(self.astart)

    async def acquire_stream(self, x: Acquisition) -> AsyncGenerator[DataEvent, None]:

        events_queue = self.compiler(x, self.system_config)
        async with self._lock:
            for paired_events in events_queue:
                for paired_event in paired_events:
                    async for event in self.system_config.managers[
                        paired_event.manager
                    ].compute_event(paired_event.event):
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

        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        self._lock = None
        set_current_engine(None)
        pass

    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True
