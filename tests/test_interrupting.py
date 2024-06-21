import pytest

from akuire.acquisition import AcquisitionResult
from akuire.composition.composer import arun
from akuire.composition.helpers import achain, ainterupting, amerge, auntil
from akuire.events.data_event import DataEvent, ZipEvent
from akuire.helpers.base import acquire_z_stack, one_shot_snap
from akuire.managers.testing.errors import TestableError


@pytest.mark.asyncio
@pytest.mark.composition
async def test_composition_run_until_condition(dual_camera_engine):

    z_stacks = []

    async def acheck_conditions(event):
        """Gather the z stacks in a list"""
        z_stacks.append(event)
        if len(z_stacks) == 2:
            return True

    async with dual_camera_engine as e:
        result = await arun(
            auntil(
                acquire_z_stack(device="virtual_camera1", item_exposure_time=0.1),
                acheck_conditions,
            )
        )

        assert isinstance(result, AcquisitionResult)
        assert len(result.collected_events) == 2


@pytest.mark.asyncio
@pytest.mark.composition
async def test_interrupting(dual_camera_engine):

    async with dual_camera_engine as e:

        async def condition(event: DataEvent):
            return event.device == "virtual_camera2"

        result = await arun(
            ainterupting(
                achain(
                    one_shot_snap(device="virtual_camera1"),
                    one_shot_snap(device="virtual_camera2"),
                    one_shot_snap(device="virtual_camera1"),
                ),
                acquire_z_stack(device="virtual_camera2", item_exposure_time=0.1),
                condition,
                restarts=None,
            )
        )

        assert isinstance(result, AcquisitionResult)
        assert len(result.collected_events) == 11
