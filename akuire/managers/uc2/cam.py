import asyncio
import dataclasses
import io
from typing import AsyncContextManager, AsyncGenerator
import typing
from urllib.parse import urlencode

import aiohttp
import numpy as np
import PIL.Image
import urllib3

from akuire.events import (
    AcquireFrameEvent,
    DataEvent,
    ImageDataEvent,
)
from akuire.events.manager_event import (
    ArmEvent,
    DisarmEvent,
    SetLightIntensityEvent,
    LiveCameraEvent,
)
from akuire.managers.base import BaseManager
import gxipy as gx


@dataclasses.dataclass
class DahengImagingManager(BaseManager):
    """Manager for the OpenUC2 REST API

    This manager is used to control the OpenUC2 REST API.
    It can be used to control the LED matrix, the positioner and the camera.

    """

    exposition_time_is_sleep: bool = False

    _gx_manager: gx.DeviceManager | None = None
    _is_armed: bool = False
    _cam: typing.Any | None = None

    async def __aenter__(self) -> AsyncContextManager[BaseManager]:
        self._gx_manager = gx.DeviceManager()
        self._cam = self._gx_manager.open_device_by_index(1)

    async def acquire_frame(self, event: AcquireFrameEvent) -> np.ndarray:
        """Acquire a frame from the camera

        This method acquires a frame from the camera and returns it as a numpy array.

        Args:
            event (AcquireFrameEvent): The event that triggered the acquisition

        Returns:
            np.ndarray: The acquired frame

        """
        raw_image = self._cam.data_stream[0].get_image()

        convert_image = raw_image.convert("RGB")
        # Get the numpy array
        image = np.array(convert_image.get_numpy_array())
        return image

    async def compute_event(
        self, event: AcquireFrameEvent | ArmEvent | DisarmEvent | LiveCameraEvent
    ) -> AsyncGenerator[DataEvent, None]:
        if isinstance(event, ArmEvent):
            self._is_armed = True
            self._cam.stream_on()

        if isinstance(event, DisarmEvent):
            self._is_armed = False
            self._cam.stream_off()

        if isinstance(event, AcquireFrameEvent):
            assert self._gx_manager is not None
            assert self._is_armed, "The camera must be armed before acquiring a frame"
            image = await self.acquire_frame(event)
            yield ImageDataEvent(data=image, device=self.device)

        if isinstance(event, LiveCameraEvent):
            assert self._gx_manager is not None
            assert self._is_armed, "The camera must be armed before acquiring a frame"
            while True:
                image = await self.acquire_frame(event)
                yield ImageDataEvent(data=image, device=self.device)
