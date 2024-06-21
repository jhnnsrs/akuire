from functools import reduce

from akuire.acquisition import Acquisition, PairedEvent
from akuire.config import SystemConfig
from akuire.errors import AtomicException, ManagerError
from akuire.events import ManagerEvent


def recurse_transpile_until_accepted(
    current_event: ManagerEvent, config: SystemConfig
) -> list[PairedEvent]:

    set_keys = []

    for manager in config.managers:
        if current_event.device and current_event.device != manager.device:
            continue

        if manager.challenge(current_event):
            set_keys.append(manager.device)
        else:
            if current_event.device:
                raise ManagerError(
                    f"Event {current_event} cannot be handled by assigned manager {current_event.device}."
                )

    if len(set_keys) > 1:
        raise ManagerError(
            f"Event {current_event} can be handled by multiple managers."
            + str(set_keys)
            + ". Please assign the event to a specific manager."
        )
    elif len(set_keys) == 1:
        return [PairedEvent(manager=set_keys[0], event=current_event)]
    else:
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
