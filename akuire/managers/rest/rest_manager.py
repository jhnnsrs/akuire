import asyncio
import dataclasses
import io
from typing import AsyncGenerator
from urllib.parse import urlencode

import aiohttp
import numpy as np
import PIL.Image
import urllib3

from akuire.events import (
    AcquireFrameEvent,
    AcquireZStackEvent,
    DataEvent,
    HasMovedEvent,
    ImageDataEvent,
    ManagerEvent,
    MoveEvent,
    MoveXEvent,
    MoveYEvent,
    ZChangeEvent,
)
from akuire.events.manager_event import SetLightIntensityEvent
from akuire.managers.base import Manager


@dataclasses.dataclass
class OpenUC2RestManager(Manager):
    """Manager for the OpenUC2 REST API

    This manager is used to control the OpenUC2 REST API.
    It can be used to control the LED matrix, the positioner and the camera.

    """

    exposition_time_is_sleep: bool = False
    endpoint: str = "https://192.168.137.1:8002/"
    png_snap_endpoint: str = "RecordingController/snapNumpyToFastAPI/"
    set_intensity_endpoint: str = "LEDMatrixController/setIntensity/"
    set_positioner_endpoint: str = "PositionerController/movePositioner"
    ssl: bool = False
    stage = "ESP32Stage"

    async def compute_event(
        self, event: AcquireFrameEvent | ZChangeEvent | MoveXEvent | MoveYEvent
    ) -> AsyncGenerator[DataEvent, None]:

        if isinstance(event, AcquireFrameEvent):
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.endpoint + self.png_snap_endpoint,
                    ssl=self.ssl,
                ) as response:
                    # Download the file
                    # Convert the response to a PIL image
                    bytes_array = await response.read()

                    # Bytes array to image
                    image = PIL.Image.open(io.BytesIO(bytes_array))
                    # to numpy array
                    image = np.array(image)
                    x = np.reshape(image, (1, 1, 1, *image.shape))
                    print(x)
                    yield ImageDataEvent(data=x)

        if isinstance(event, SetLightIntensityEvent):
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.endpoint
                    + self.set_intensity_endpoint
                    + "?intensity="
                    + str(int(event.intensity * 255)),
                    ssl=self.ssl,
                ) as response:
                    # Download the file
                    t = await response.read()
                    print(t)

        if isinstance(event, MoveEvent):
            async with aiohttp.ClientSession() as session:

                if event.x is not None:
                    querystring = urlencode(
                        [
                            ("positionerName", self.stage),
                            ("axis", "X"),
                            ("dist", event.x),
                            ("speed", event.speed),
                            ("isBlocking", True),
                            ("isAbsolute", True),
                        ]
                    )

                    url = (
                        self.endpoint + self.set_positioner_endpoint + "?" + querystring
                    )

                    print(url)

                    async with session.get(
                        url,
                        ssl=self.ssl,
                    ) as response:
                        # Download the file
                        t = await response.read()
                        print(t)

                if event.y is not None:
                    querystring = urlencode(
                        [
                            ("positionerName", self.stage),
                            ("axis", "Y"),
                            ("dist", event.y),
                            ("speed", event.speed),
                            ("isBlocking", True),
                            ("isAbsolute", True),
                        ]
                    )

                    url = (
                        self.endpoint + self.set_positioner_endpoint + "?" + querystring
                    )

                    print(url)

                    async with session.get(
                        url,
                        ssl=self.ssl,
                    ) as response:
                        # Download the file
                        t = await response.read()
                        print(t)

                yield HasMovedEvent(x=event.x, y=event.y)

    def challenge(self, event: ManagerEvent) -> bool:
        if isinstance(event, AcquireFrameEvent):
            return True
        if isinstance(event, ZChangeEvent):
            return True
        if isinstance(event, MoveXEvent):

            return True

        if isinstance(event, MoveEvent):
            return True
        if isinstance(event, MoveYEvent):
            return True
        if isinstance(event, SetLightIntensityEvent):
            return True
