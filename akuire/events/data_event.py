import dataclasses
import time

import numpy as np


@dataclasses.dataclass(kw_only=True)
class DataEvent:
    """Base class for all data events

    Data events are used to communicate data that are
    generated during the acquisition process. This
    can be images, metadata, or other data that is
    generated during the acquisition process.


    """

    device: str
    timestamp: float = dataclasses.field(default_factory=time.time, init=False)


@dataclasses.dataclass(kw_only=True)
class ComposedEvent(DataEvent):
    pass


@dataclasses.dataclass(kw_only=True)
class ZipEvent(ComposedEvent):
    events: list[DataEvent]

    @property
    def first(self):
        return self.events[0]

    @property
    def second(self):
        return self.events[1]

    @property
    def third(self):
        return self.events[2]


@dataclasses.dataclass(kw_only=True)
class UncollectedBufferEvent(ComposedEvent):
    buffer: list[list[DataEvent]]

    @property
    def first(self):
        return self.buffer[0]

    @property
    def second(self):
        return self.buffer[1]

    @property
    def third(self):
        return self.buffer[2]


@dataclasses.dataclass(kw_only=True)
class ImageDataEvent(DataEvent):
    data: np.ndarray
    """Data should be 5 Dimensional c,t,z,y,x"""


@dataclasses.dataclass(kw_only=True)
class HasMovedEvent(DataEvent):
    x: float | None = None
    y: float | None = None
    z: float | None = None
    pass
    pass
