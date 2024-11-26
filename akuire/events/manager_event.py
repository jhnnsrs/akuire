import dataclasses
from functools import reduce
from operator import add

from akuire.errors import AtomicException


@dataclasses.dataclass(kw_only=True)
class ManagerEvent:
    device: str | None = None

    def transpile(self) -> list["ManagerEvent"]:
        raise AtomicException(
            f"{self.__class__.__name__} even is atomic and cannot be transpiled."
        )


@dataclasses.dataclass(kw_only=True)
class DelayEvent(ManagerEvent):
    timeout: float


@dataclasses.dataclass(kw_only=True)
class DeviceChangeEvent(ManagerEvent):
    device: str
    state: bool


@dataclasses.dataclass(kw_only=True)
class ArmEvent(ManagerEvent):
    pass


@dataclasses.dataclass(kw_only=True)
class DisarmEvent(ManagerEvent):
    pass


@dataclasses.dataclass(kw_only=True)
class LiveCameraEvent(ManagerEvent):
    pass


@dataclasses.dataclass(kw_only=True)
class AcquireFrameEvent(ManagerEvent):
    exposure_time: float = dataclasses.field(default=0.1)


@dataclasses.dataclass(kw_only=True)
class MoveZEvent(ManagerEvent):
    step: int
    speed: int = 1000


@dataclasses.dataclass(kw_only=True)
class AcquireZStackEvent(ManagerEvent):
    z_step: float = 100
    z_steps: int
    item_exposure_time: float

    def transpile(self) -> list[ManagerEvent]:
        print("Transpiling z stack")

        z_stack_events = []

        z_stack_events.append(ArmEvent())

        for i in range(self.z_steps):
            z_stack_events += [
                AcquireFrameEvent(exposure_time=self.item_exposure_time),
                MoveZEvent(step=i * self.z_step),
            ]

        z_stack_events.append(DisarmEvent())

        return z_stack_events


@dataclasses.dataclass(kw_only=True)
class AcquireTSeriesEvent(ManagerEvent):
    t_steps: float
    interval: float = 10
    item_exposure_time: float = 100

    def transpile(self) -> list[ManagerEvent]:
        print("Transpiling z stack")
        t_series_events = []

        t_series_events.append(ArmEvent())

        for i in range(self.t_steps):
            t_series_events += [
                AcquireFrameEvent(exposure_time=self.item_exposure_time),
                DelayEvent(timeout=self.interval),
            ]

        t_series_events.append(DisarmEvent())

        return t_series_events


@dataclasses.dataclass(kw_only=True)
class MoveEvent(ManagerEvent):
    x: float | None = None
    y: float | None = None
    z: float | None = None
    speed: float = 10000

    def transpile(self) -> list[ManagerEvent]:
        return [MoveXEvent(x=self.x), MoveYEvent(y=self.y)]


@dataclasses.dataclass(kw_only=True)
class MoveXEvent(ManagerEvent):
    step: int
    speed: int = 10000


@dataclasses.dataclass(kw_only=True)
class GetXEvent(ManagerEvent):
    pass


@dataclasses.dataclass(kw_only=True)
class SetLightIntensityEvent(ManagerEvent):
    intensity: float


@dataclasses.dataclass(kw_only=True)
class SetLaserStateEvent(ManagerEvent):
    on: bool


@dataclasses.dataclass(kw_only=True)
class MoveYEvent(ManagerEvent):
    step: int
    speed: int = 10000
    pass
