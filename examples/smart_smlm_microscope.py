""" Example of using the virtual SMLM microscope manager to acquire a time series of images. 


This example demonstrates how to use the virtual SMLM microscope manager to acquire a time series of images and
analysis the images in real-time as they are being acquired. Here we optmize the acquisition by using the
ESRRF metric.


Note: While you can also could send singular acquire frame events to the virtual SMLM microscope manager, 
this example demonstrates how to acquire a time series of images using the higher lever AcquireTSeriesEvent, 
which can be implemented by any devices that in turn used to set up  an optimized acquistion on the Microscope 
(e.g. acquiring a time series of images through hardware triggering, etc.). The event stream lets you then
react to the acquired images in real-time, even in this optimized acquisition mode.






"""

import asyncio

import numpy as np

from akuire.acquisition import Acquisition
from akuire.compilers.default import compile_events
from akuire.config import SystemConfig
from akuire.engine import AcquisitionEngine
from akuire.events import AcquireTSeriesEvent
from akuire.events.data_event import ImageDataEvent
from akuire.managers.virtual.smlm_microscope import SMLMMicroscope

# Set the threshold for detecting a scream
THRESHOLD = 0.5


def check_performance_metric(collected_frames: list[np.ndarray]):
    """Check the ESRRF metric of an image.



    Args:
        image (np.ndarray): The image to check

    Returns:
        float: The ESRRF metric of the image
    """

    # Here we would implement the ESRRF metric
    # TODO: Implement the ESRRF metric
    return 1 if len(collected_frames) > 10 else 0


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

        collected_frames = []

        async for i in e.acquire_stream(x):

            if isinstance(i, ImageDataEvent):
                collected_frames.append(i.data)
                metric = await asyncio.to_thread(
                    check_performance_metric, collected_frames
                )

                print(f"ESRRF: {metric}")
                if metric > THRESHOLD:
                    print("Otimized acquisition. We are done!")
                    return collected_frames


if __name__ == "__main__":

    x = asyncio.run(acquire_snap())
