from functools import reduce

from akuire.acquisition import Acquisition, PairedEvent
from akuire.config import SystemConfig
from akuire.errors import AtomicException
from akuire.events import ManagerEvent


def recurse_transpile_until_accepted(
    current_event: ManagerEvent, config: SystemConfig
) -> list[PairedEvent]:

    for key, manager in config.managers.items():
        if manager.challenge(current_event):
            return [PairedEvent(manager=key, event=current_event)]

    print(current_event)
    return reduce(
        lambda x, y: x + y,
        [
            recurse_transpile_until_accepted(event, config)
            for event in current_event.transpile()
        ],
        [],
    )


def compile_events(x: Acquisition, config: SystemConfig) -> list[list[PairedEvent]]:

    manager_queue = []

    for event in x.events:
        try:
            parsable_events = recurse_transpile_until_accepted(event, config)
            print(parsable_events)

            manager_queue.append(parsable_events)
        except AtomicException as e:
            raise AtomicException(
                f"Event {event} cannot be transpiled to an event that can be handled by any Manager."
            ) from e

    return manager_queue
