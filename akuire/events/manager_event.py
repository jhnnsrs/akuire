import dataclasses
from functools import reduce
from operator import add

from akuire.errors import AtomicException


@dataclasses.dataclass
class ManagerEvent:
    pass

    def transpile(self) -> list["ManagerEvent"]:
        raise AtomicException(
            f"{self.__class__.__name__} even is atomic and cannot be transpiled."
        )


@dataclasses.dataclass
class DeviceChangeEvent(ManagerEvent):
    device: str
    state: bool


@dataclasses.dataclass
class AcquireFrameEvent(ManagerEvent):
    exposure_time: float = 100


@dataclasses.dataclass
class ZChangeEvent(ManagerEvent):
    z: float


@dataclasses.dataclass
class AcquireZStackEvent(ManagerEvent):
    z_steps: float
    item_exposure_time: float

    def transpile(self) -> list[ManagerEvent]:
        print("Transpiling z stack")
        x = reduce(
            lambda x, y: list(x) + list(y),
            list(
                zip(
                    [
                        AcquireFrameEvent(exposure_time=self.item_exposure_time)
                        for x in range(self.z_steps)
                    ],
                    [ZChangeEvent(z=i) for i in range(self.z_steps)],
                )
            ),
            [],
        )

        print(x)

        return x


@dataclasses.dataclass
class AcquireTSeriesEvent(ManagerEvent):
    t_steps: float
    interval: float | None = None
    item_exposure_time: float = 100

    def transpile(self) -> list[ManagerEvent]:
        print("Transpiling z stack")

        return [
            AcquireFrameEvent(exposure_time=self.item_exposure_time)
            for t in range(self.t_steps)
        ]


@dataclasses.dataclass
class MoveEvent(ManagerEvent):
    x: float | None = None
    y: float | None = None
    z: float | None = None
    speed: float = 10000

    def transpile(self) -> list[ManagerEvent]:
        return [MoveXEvent(x=self.x), MoveYEvent(y=self.y)]


@dataclasses.dataclass
class MoveXEvent(ManagerEvent):
    x: float


@dataclasses.dataclass
class GetXEvent(ManagerEvent):
    pass


@dataclasses.dataclass
class SetLightIntensityEvent(ManagerEvent):
    intensity: float


@dataclasses.dataclass
class MoveYEvent(ManagerEvent):
    y: float
    pass
