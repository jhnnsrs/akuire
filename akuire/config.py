import dataclasses

from akuire.managers.base import Manager


@dataclasses.dataclass
class SystemConfig:
    """Configuration for the system.

    A system is composed of multiple managers. This class holds the configuration for the system.
    , in the form of a dictionary of managers.



    """

    managers: list[Manager]

    def get_manager(self, device_name: str) -> Manager:
        """Get a manager by name.

        Args:
            manager_name (str): The name of the manager to get.

        Returns:
            Manager: The manager with the given name.

        """
        for manager in self.managers:
            if manager.device == device_name:
                return manager
        raise ValueError(f"Manager {device_name} not found")
