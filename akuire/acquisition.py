import dataclasses
from typing import List

import numpy as np

from akuire.events import ManagerEvent
from akuire.events.data_event import DataEvent, ImageDataEvent


@dataclasses.dataclass
class PairedEvent:
    manager: str
    event: ManagerEvent


@dataclasses.dataclass
class Acquisition:
    events: List[ManagerEvent]
    context: dict = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class AcquisitionResult:
    """Class to store the result of an acquisition

    This class is used to store the result of an acquisition. It contains the collected events and
    provides a method to stack the collected ImageDataEvents into a single Z-stack.

    Attributes:
        collected_events (List[DataEvent]): List of DataEvents that were collected during the acquisition





    """

    collected_events: List[DataEvent]

    def to_z_stack(self):
        """Stack the collected ImageDataEvents into a single Z-stack

        This method stacks the collected ImageDataEvents into a single Z-stack. It will raise a ValueError if none of the
        collected events are ImageDataEvents.
        """
        try:
            return np.stack(
                [
                    x.data
                    for x in self.collected_events
                    if isinstance(x, ImageDataEvent)
                ],
                axis=0,
            )
        except ValueError as e:
            print(self.collected_events)
            raise ValueError(
                "Not all collected events are ImageDataEvents, cannot stack. Check the collected events."
            ) from e
