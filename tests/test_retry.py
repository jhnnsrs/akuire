import numpy as np
import pytest

from akuire.acquisition import Acquisition, AcquisitionResult
from akuire.compilers.default import compile_events
from akuire.config import SystemConfig
from akuire.engine import AcquisitionEngine
from akuire.events import AcquireZStackEvent, ImageDataEvent, MoveEvent
from akuire.managers.testing import (
    NonSweepableCamera,
    SweepableCamera,
    VirtualStageManager,
    ZStageManager,
)


async def oh_i_faild(event):

    raise Exception("Oh i failed")


@pytest.mark.asyncio
async def test_retry(default_engine):

    x = Acquisition(
        events=[
            MoveEvent(x=1, y=2),
            AcquireZStackEvent(z_steps=30, item_exposure_time=0.001),
        ]
    )
    async with default_engine as e:
        try:

            result = await e.acquire(x, [oh_i_faild])
        except Exception:
            print("Failed to acquire image, retrying")
            result = await e.acquire(
                x,
            )

        assert isinstance(result, AcquisitionResult)
