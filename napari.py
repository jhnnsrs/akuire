import asyncio
from functools import reduce
from operator import add

import cv2
import NanoImagingPack as nip
import numpy as np
import sounddevice as sd

import napari
from akuire.acquisition import Acquisition, AcquisitionResult
from akuire.compilers.default import compile_events
from akuire.config import SystemConfig
from akuire.engine import AcquisitionEngine
from akuire.events import (
    AcquireFrameEvent,
    AcquireTSeriesEvent,
    AcquireZStackEvent,
    MoveEvent,
    SetLightIntensityEvent,
)
from akuire.events.data_event import ImageDataEvent
from akuire.helpers import one_shot_snap
from akuire.managers.rest.rest_manager import OpenUC2RestManager
from akuire.managers.testing import (
    NonSweepableCamera,
    SweepableManager,
    VirtualStageManager,
    ZStageManager,
)
from akuire.managers.virtual.smlm_microscope import SMLMMicroscope


async def acquire_snap():
    async with AcquisitionEngine(
        system_config=SystemConfig(
            managers={
                "virtual_camera": SMLMMicroscope(),
            }
        ),
        compiler=compile_events,
    ) as e:

        x = Acquisition(events=[AcquireTSeriesEvent(t_steps=10)])

        async for i in e.acquire_stream(x):

            if isinstance(i, ImageDataEvent):
                image = i.data
                print(image.shape)


# Set the threshold for detecting a scream
THRESHOLD = 10


if __name__ == "__main__":

    x = asyncio.run(acquire_snap())
