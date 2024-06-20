import asyncio

import numpy as np
import pytest

from akuire.acquisition import Acquisition, AcquisitionResult
from akuire.compilers.default import compile_events
from akuire.config import SystemConfig
from akuire.engine import AcquisitionEngine
from akuire.events import AcquireZStackEvent, ImageDataEvent, MoveEvent
from akuire.managers.testing import (
    NonSweepableCamera,
    SweepableManager,
    VirtualStageManager,
    ZStageManager,
)

positions = [
    (1, 2),
    (3, 4),
    (5, 6),
    (7, 8),
    (9, 10),
    (11, 12),
    (13, 14),
    (15, 16),
    (17, 18),
    (19, 20),
]


async def long_running_segmentation(data: np.array):
    x = [
        Acquisition(
            events=[
                MoveEvent(x=np.random.randint(0, 100), y=np.random.randint(0, 100)),
                AcquireZStackEvent(z_steps=30, item_exposure_time=0.1),
            ]
        )
        for i in range(np.random.randint(0, 10))
    ]
    return x


async def amonitor_position(e, x: 1, y: 2):

    x = Acquisition(
        events=[
            MoveEvent(x=1, y=2),
            AcquireZStackEvent(z_steps=30, item_exposure_time=0.1),
        ]
    )

    result = await e.acquire(x, [])

    print(result)
    events = await long_running_segmentation(result.to_z_stack())

    for i in events:
        await e.acquire(i)


@pytest.mark.asyncio
async def test_segmentation_multip(default_engine):

    x = Acquisition(
        events=[
            MoveEvent(x=1, y=2),
            AcquireZStackEvent(z_steps=30, item_exposure_time=0.1),
        ]
    )
    async with default_engine as e:

        monitoring_tasks = []
        for i in positions:
            monitoring_tasks.append(asyncio.create_task(amonitor_position(e, *i)))

        await asyncio.gather(*monitoring_tasks)
