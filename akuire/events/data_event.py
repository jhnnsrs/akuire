import dataclasses

import numpy as np


@dataclasses.dataclass
class DataEvent:
    """Base class for all data events

    Data events are used to communicate data that are
    generated during the acquisition process. This
    can be images, metadata, or other data that is
    generated during the acquisition process.


    """

    pass


@dataclasses.dataclass
class ImageDataEvent(DataEvent):

    data: np.ndarray
    """Data should be 5 Dimensional c,t,z,y,x"""


@dataclasses.dataclass
class HasMovedEvent(DataEvent):
    x: float | None = None
    y: float | None = None
    z: float | None = None
    pass
    pass
