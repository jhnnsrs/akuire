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
from akuire.managers.testing.faulty_camera import FaultyCamera


@pytest.fixture
def default_engine():
    engine = AcquisitionEngine(
        system_config=SystemConfig(
            managers=[
                SweepableCamera("virtual_camera"),
                ZStageManager("z_stage"),
                VirtualStageManager("virtual_stage"),
            ]
        ),
        compiler=compile_events,
    )

    return engine


@pytest.fixture
def faulty_engine():
    engine = AcquisitionEngine(
        system_config=SystemConfig(
            managers=[
                FaultyCamera("virtual_camera"),
            ]
        ),
        compiler=compile_events,
    )

    return engine


@pytest.fixture
def dual_camera_engine():
    engine = AcquisitionEngine(
        system_config=SystemConfig(
            managers=[
                SweepableCamera("virtual_camera1"),
                SweepableCamera("virtual_camera2"),
            ]
        ),
        compiler=compile_events,
    )

    return engine
