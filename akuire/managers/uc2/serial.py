from uc2rest import UC2Client
import asyncio
from uc2rest import UC2Client

from akuire.events.data_event import FinishedEvent
from akuire.events.manager_event import (
    MoveXEvent,
    MoveYEvent,
    MoveZEvent,
    SetLaserStateEvent,
    SetLightIntensityEvent,
)
from akuire.managers.base import BaseManager


class SerialUC2Manager(BaseManager):
    serialport: str = "/dev/ttyUSB0"
    baudrate: int = 115200
    n_leds: int = 64
    _client: UC2Client | None = None

    def setup_client(self):
        self._client = UC2Client(
            serialport=self.serialport,
            baudrate=self.baudrate,
            NLeds=self.n_leds,
            DEBUG=True,
        )

    async def __aenter__(self):
        print("Entering")
        await asyncio.to_thread(self.setup_client)
        print("Entered")

    async def compute_event(
        self, event: MoveXEvent | MoveYEvent | MoveZEvent | SetLightIntensityEvent
    ):
        if isinstance(event, MoveXEvent):
            await asyncio.to_thread(
                self._client.motor.move_x,
                steps=event.step,
                speed=event.speed,
                is_blocking=True,
                is_absolute=True,
                is_enabled=True,
            )
            yield FinishedEvent(device=self.device)
        if isinstance(event, MoveYEvent):
            await asyncio.to_thread(
                self._client.motor.move_y,
                steps=event.step,
                speed=event.speed,
                is_blocking=True,
                is_absolute=True,
                is_enabled=True,
            )
            yield FinishedEvent(device=self.device)

        if isinstance(event, MoveZEvent):
            await asyncio.to_thread(
                self._client.motor.move_z,
                steps=event.step,
                speed=event.speed,
                is_blocking=True,
                is_absolute=True,
                is_enabled=True,
            )
            yield FinishedEvent(device=self.device)

        if isinstance(event, SetLightIntensityEvent):
            await asyncio.to_thread(
                self._client.laser.set_laser,
                channel=1,
                value=event.intensity,
                is_blocking=True,
            )

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        print("Exiting")
        await asyncio.to_thread(self._client.close)
        print("Exited")
