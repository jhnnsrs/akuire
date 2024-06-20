import dataclasses

from akuire.managers.base import Manager


@dataclasses.dataclass
class SystemConfig:
    """Configuration for the system.

    A system is composed of multiple managers. This class holds the configuration for the system.
    , in the form of a dictionary of managers.



    """

    managers: dict[str, Manager]
