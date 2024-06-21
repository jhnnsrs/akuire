""" This example demonstrates how to smartly follow a path on a microscope slide. 

This example uses the virtual microscope manager to acquire a time series of images and
 calculates the direction to move the microscope to follow a line on the slide.

It was designed during the 2024 Smart Microscope Hackathon to illustrate a common
use case for smart microscopes. While the actual logic for following a path needs
some refinement per use case, this example demonstrates the basic concept.

"""

import asyncio

import cv2
import NanoImagingPack as nip
import numpy as np
import sounddevice as sd

import smlm_microscope
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


def calculate_shift(image: np.ndarray) -> tuple[float, float]:
    """Calculate the direction to move the microscope to follow a line

    #TODO: Make this more stable

    """

    Ny, Nx = image.shape
    mBinary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    mBinary = nip.gaussf(cv2.erode(mBinary, None, iterations=20), 50)

    # detect max along short axis
    pxX = np.array(np.argmax(mBinary, 1))
    pxY = np.arange(0, pxX.shape[0])

    mFct = np.poly1d(np.polyfit(pxY, pxX, 1))
    # %
    dy = Ny // 2
    dx = mFct(dy) - mFct(Nx // 2)
    mText = (
        "We are moving the microscope in x:/y: "
        + str(round(dx, 2))
        + " / "
        + str(round(dy, 2))
    )
    print(mText)
    return dx, dy

    # optional: Think about PID?


from akuire.managers.rest.rest_manager import OpenUC2RestManager


async def acquire_snap():
    async with AcquisitionEngine(
        system_config=SystemConfig(
            managers={
                "virtual_camera": OpenUC2RestManager(),
            }
        ),
        compiler=compile_events,
    ) as e:

        # Start at a fixed position
        position_x, position_y = 800, 800

        images = []

        for i in range(20):
            # Acquire a frame and calculate the shift

            result = await e.acquire(
                Acquisition(
                    events=[
                        MoveEvent(x=position_x, y=position_y),
                        AcquireFrameEvent(),
                    ]
                )
            )

            frame = result.to_z_stack()[0, 0, 0, 0, :, :]
            dx, dy = calculate_shift(frame)
            position_x = position_x + dx
            position_y = position_y + dy

            # Move the microscope to the new position
            images.append(frame)

        return np.stack(images)


if __name__ == "__main__":

    x = asyncio.run(acquire_snap())
