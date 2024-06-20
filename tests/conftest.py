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


@pytest.fixture
def default_engine():
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

    return engine
