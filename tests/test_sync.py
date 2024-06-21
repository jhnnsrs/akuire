import numpy as np
import pytest

from akuire.acquisition import Acquisition, AcquisitionResult
from akuire.compilers.default import compile_events
from akuire.config import SystemConfig
from akuire.engine import AcquisitionEngine
from akuire.events import AcquireZStackEvent, DataEvent, ImageDataEvent, MoveEvent
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


@pytest.mark.parametrize("engine", create_some_engines())
def test_acquistion_engine(engine):

    x = Acquisition(
        events=[
            MoveEvent(x=1, y=2),
            AcquireZStackEvent(z_steps=30, item_exposure_time=0.1),
        ]
    )

    with engine as e:
        result = e.acquire_sync(x)
        assert isinstance(result, AcquisitionResult)
        assert isinstance(result.to_z_stack(), np.ndarray)


@pytest.mark.parametrize("engine", create_some_engines())
def test_acquistion_engine(engine):

    x = Acquisition(
        events=[
            MoveEvent(x=1, y=2),
            AcquireZStackEvent(z_steps=30, item_exposure_time=0.1),
        ]
    )

    with engine as e:
        for i in e.acquire_stream_sync(x):
            assert isinstance(i, DataEvent)
