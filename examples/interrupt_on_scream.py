import asyncio
from functools import partial, reduce
from operator import add

import napari
import numpy as np
import sounddevice as sd

from akuire.acquisition import Acquisition, AcquisitionResult
from akuire.compilers.default import compile_events
from akuire.config import SystemConfig
from akuire.engine import AcquisitionEngine
from akuire.events import (
    AcquireFrameEvent,
    AcquireZStackEvent,
    MoveEvent,
    SetLightIntensityEvent,
)
from akuire.managers.rest.rest_manager import RestManager
from akuire.managers.testing import (
    NonSweepableCamera,
    SweepableManager,
    VirtualStageManager,
    ZStageManager,
)

# Set the threshold for detecting a scream
THRESHOLD = 10
buffer = []


async def acquire_snap():
    engine = AcquisitionEngine(
        system_config=SystemConfig(
            managers={
                "virtual_camera": RestManager(),
            }
        ),
        compiler=compile_events,
    )

    acquisition_events = reduce(
        add,
        [
            [
                SetLightIntensityEvent(intensity=0.1 * i),
                MoveEvent(x=300 + (500 * i), y=200 + (500 * i)),
                AcquireFrameEvent(),
            ]
            for i in range(10)
        ],
        [],
    )

    x = Acquisition(events=acquisition_events)

    try:
        async with engine as e:
            print("Acquiring snap")
            result = await e.acquire(x)

            print(result)
            assert isinstance(result, AcquisitionResult)
            return result
    except asyncio.CancelledError as e:
        print("Cancelled")
        return None


def cancel_on_stream(task: asyncio.Task, indata, frames, time, status):
    volume_norm = np.linalg.norm(indata) * 10
    if volume_norm > THRESHOLD:
        #
        buffer.append(indata)
    else:
        buffer.clear()

    if len(buffer) == 10:
        # Only on consecutive screams
        print("Scream detected!")

        if not task.done():
            # task.cancel()
            pass


async def controll():
    task = asyncio.create_task(acquire_snap())

    # Open the microphone stream
    with sd.InputStream(callback=partial(cancel_on_stream, task)):
        print("Listening for screams...")
        return await task


if __name__ == "__main__":

    x = asyncio.run(controll())

    napari.view_image(x.to_z_stack())
    napari.run()
