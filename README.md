# akuire

[![codecov](https://codecov.io/gh/jhnnsrs/akuire/branch/master/graph/badge.svg?token=UGXEA2THBV)](https://codecov.io/gh/jhnnsrs/akuire)
[![PyPI version](https://badge.fury.io/py/akuire.svg)](https://pypi.org/project/akuire/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://pypi.org/project/akuire/)
![Maintainer](https://img.shields.io/badge/maintainer-jhnnsrs-blue)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/akuire.svg)](https://pypi.python.org/pypi/akuire/)
[![PyPI status](https://img.shields.io/pypi/status/akuire.svg)](https://pypi.python.org/pypi/akuire/)

[![Akuire Logo](./akuire.png)](./akuire.png)

Akuire is a prototype of asynchronous acquisiton engine for smart-microscopy workflows. It was designed during the "Smart Microscopy" hackathon at the [Lund](https://www.lunduniversity.lu.se/) [Bioimaging Center](https://www.bmc.lu.se/). 

The main goal of Akuire is to provide a simple and flexible way to acquire images from a microscope in an asynchronous way, interfacing with different
microscopy software backbones. 

## Installation

To install Akuire, you can use pip:

```bash

pip install akuire

```

## Usage

To use Akuire, you need to create an instance of the `AcquistionEinge` class, passing the desired device managers and the system settings.
You can use the acquisition engine to acquire images from the microscope through predefined plans in an `Acquisition` object.

```python
from akuire import AcquisitionEngine, Acquisition, MoveEvent, AcquireZStackEvent, SystemConfig
from akuire.managers.testing import NonSweepableCamera, ZStageManager, VirtualStageManager
import asyncio

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


x = Acquisition(
    events=[
        MoveEvent(x=1, y=2),
        AcquireZStackEvent(z_steps=30, item_exposure_time=0.1),
    ]
)
# The acquisition plan is compiled into a list of events



async def main():
    async with engine as e:

        # A blocking operation that acquires the ZStack
        # The event plan will be "compiled" into a list of events
        # that are compatible with the underlying hardware
        # trying to optimize the acquisition process
        result = await e.acquire(x)
        # result is a ZStack object
        
        # A hyperstack can be created from the ZStack object
        stack = result.to_z_stack()


if __name__ == "__main__":
    asyncio.run(main())
```

## Documentation

Right now this is the only documentation available. More documentation will be added in the future.
If you are interested in potential use cases, please check the [examples](examples) folder.




## Contributing

Pull requests are welcome. Happy for any feedback or suggestions.



## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.