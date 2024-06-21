import pytest

from akuire.acquisition import AcquisitionResult
from akuire.composition.composer import arun
from akuire.composition.helpers import achain, amerge, auntil, azip
from akuire.events.data_event import DataEvent, ZipEvent
from akuire.helpers.base import acquire_z_stack, one_shot_snap
from akuire.managers.testing.errors import TestableError


@pytest.mark.asyncio
@pytest.mark.composition
async def test_composition(default_engine):

    async with default_engine as e:
        async for event in achain(one_shot_snap(), one_shot_snap()):
            assert isinstance(event, DataEvent)


@pytest.mark.asyncio
@pytest.mark.composition
async def test_composition_run(default_engine):

    async with default_engine as e:
        result = await arun(achain(one_shot_snap(), one_shot_snap()))
        assert isinstance(result, AcquisitionResult)
        assert len(result.collected_events) == 2


@pytest.mark.asyncio
@pytest.mark.composition
async def test_composition_run_with_amerge(default_engine):

    async with default_engine as e:
        result = await arun(amerge(one_shot_snap(), one_shot_snap(exposure_time=1)))
        assert isinstance(result, AcquisitionResult)
        assert len(result.collected_events) == 2


@pytest.mark.asyncio
@pytest.mark.composition
async def test_composition_run_with_azip(default_engine):

    x = one_shot_snap(exposure_time=1)
    y = one_shot_snap(exposure_time=1)

    async with default_engine as e:
        result = await arun(azip(x, y))
        assert isinstance(result, AcquisitionResult)
        assert len(result.collected_events) == 1
        assert isinstance(result.collected_events[0], ZipEvent)
        assert (
            result.collected_events[0].first.timestamp
            < result.collected_events[0].second.timestamp
        ), "The default engine has a lock so should not be able to run in parallel"


@pytest.mark.asyncio
@pytest.mark.composition
async def test_composition_run_with_azip(faulty_engine):

    with pytest.raises(TestableError):
        async with faulty_engine as e:
            result = await arun(
                amerge(one_shot_snap(exposure_time=4), one_shot_snap(exposure_time=1))
            )


@pytest.mark.asyncio
@pytest.mark.composition
async def test_composition_run_with_amerge_parallelizable(dual_camera_engine):

    async with dual_camera_engine as e:
        result = await arun(
            amerge(
                one_shot_snap(exposure_time=1, device="virtual_camera1"),
                one_shot_snap(exposure_time=0.4, device="virtual_camera2"),
            )
        )

        assert isinstance(result, AcquisitionResult)
        assert len(result.collected_events) == 2
        assert isinstance(result.collected_events[0], DataEvent)
        assert (
            result.collected_events[0].device == "virtual_camera2"
        ), "The fastest camera should be first"
        assert isinstance(result.collected_events[1], DataEvent)
        assert (
            result.collected_events[1].device == "virtual_camera1"
        ), "The slowest camera should be second"
