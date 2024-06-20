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


def create_some_engines():
    """Create some engines for testing"""
    engine = AcquisitionEngine(
        system_config=SystemConfig(
            managers={
                "virtual_camera": NonSweepableCamera(),
                "virtual_z_stage": ZStageManager(),
                "virtual_stage": VirtualStageManager(),
            }
        ),
        compiler=compile_events,
    )

    another_engine = AcquisitionEngine(
        system_config=SystemConfig(
            managers={
                "virtual_camera": SweepableManager(),
                "virtual_stage": VirtualStageManager(),
            }
        ),
        compiler=compile_events,
    )

    return engine, another_engine


@pytest.mark.asyncio
@pytest.mark.parametrize("engine", create_some_engines())
async def test_acquistion_engine(engine):

    x = Acquisition(
        events=[
            MoveEvent(x=1, y=2),
            AcquireZStackEvent(z_steps=30, item_exposure_time=0.1),
        ]
    )

    async with engine as e:
        result = await e.acquire(x)
        assert isinstance(result, AcquisitionResult)
        assert isinstance(result.to_z_stack(), np.ndarray)
