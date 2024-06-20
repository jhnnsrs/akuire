import dataclasses

import numpy as np


@dataclasses.dataclass
class DataEvent:
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
