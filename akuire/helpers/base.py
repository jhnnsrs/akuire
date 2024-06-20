from akuire.acquisition import Acquisition, AcquisitionResult
from akuire.engine import AcquisitionEngine
from akuire.events import AcquireFrameEvent
from akuire.vars import get_current_engine


async def one_shot_snap(
    exposure_time: float = 3, engine: AcquisitionEngine = None
) -> AcquisitionResult:

    engine = engine or get_current_engine()
    return await engine.acquire(Acquisition(events=[AcquireFrameEvent()]))
