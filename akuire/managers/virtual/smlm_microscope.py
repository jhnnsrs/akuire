import asyncio
import dataclasses
from typing import AsyncGenerator

import cv2
import matplotlib.pyplot as plt
import NanoImagingPack as nip
import numpy as np
from scipy.signal import convolve2d

# Use the line function from skimage
from skimage.draw import line

from akuire.assets.utils import get_absolute_path
from akuire.events import (
    AcquireFrameEvent,
    AcquireZStackEvent,
    DataEvent,
    HasMovedEvent,
    ImageDataEvent,
    ManagerEvent,
    MoveEvent,
    SetLightIntensityEvent,
    ZChangeEvent,
)
from akuire.events.manager_event import AcquireTSeriesEvent
from akuire.managers.base import Manager

try:
    import NanoImagingPack as nip

    IS_NIP = True
except:
    IS_NIP = False
import math
import os
import threading
import time

import cv2
import matplotlib.pyplot as plt
import numpy as np

# workaround to not break if numba is not installed
try:
    from numba import njit, prange
except ModuleNotFoundError:
    prange = range

    def njit(*args, **kwargs):
        def wrapper(func):
            return func

        return wrapper


# workaroung to not break if nanopyx is not installed
try:
    from nanopyx import eSRRF
except ModuleNotFoundError:

    def eSRRF(img, **kwargs):
        # if nanopyx is not installed just returns the input image
        return img


IS_NIP = True


FILE_PATH = get_absolute_path("big.jpg")


@njit(parallel=True)
def FromLoc2Image_MultiThreaded(
    xc_array, yc_array, photon_array, sigma_array, image_size, pixel_size
):
    """
    Function to generate an image from a list of emitter locations.
    Based on the DeepStorm notebook on ZeroCostDL4Mic.
    https://colab.research.google.com/github/HenriquesLab/ZeroCostDL4Mic/blob/master/Colab_notebooks/Deep-STORM_2D_ZeroCostDL4Mic.ipynb
    """
    Image = np.zeros((image_size, image_size))
    for ij in prange(image_size * image_size):
        j = int(ij / image_size)
        i = ij - j * image_size
        for xc, yc, photon, sigma in zip(xc_array, yc_array, photon_array, sigma_array):
            # Don't bother if the emitter has photons <= 0 or if Sigma <= 0
            if (photon > 0) and (sigma > 0):
                S = sigma * math.sqrt(2)
                x = i * pixel_size - xc
                y = j * pixel_size - yc
                # Don't bother if the emitter is further than 4 sigma from the centre of the pixel
                if (x + pixel_size / 2) ** 2 + (
                    y + pixel_size / 2
                ) ** 2 < 16 * sigma**2:
                    ErfX = math.erf((x + pixel_size) / S) - math.erf(x / S)
                    ErfY = math.erf((y + pixel_size) / S) - math.erf(y / S)
                    Image[j][i] += 0.25 * photon * ErfX * ErfY
    return Image


@dataclasses.dataclass
class Position:
    x: float = 0
    y: float = 0
    z: float = 0


@dataclasses.dataclass
class SMLMMicroscope(Manager):
    """A virtual SMLM microscope.

    This class simulates a virtual SMLM microscope. It generates images based on the current settings.


    """

    sensor_height: int = 512
    """The height of the sensor in pixels."""
    sensor_width: int = 512
    """The width of the sensor in pixels."""
    NA: float = 1.2
    """The numerical aperture of the microscope."""
    pixel_size: float = 0.1
    magnification: float = 2
    readout_noise: float = 50

    density: float = 0.05
    ADC_per_photon_conversion: float = 1.0
    ADC_offset: float = 100

    wave_length: float = 0.6
    wave_length_std: float = 0.5

    position: Position = dataclasses.field(default_factory=Position)
    intensity: float = 0.1
    intensity_std_dev: float = 0.01
    dz: float = 0
    image: np.ndarray = dataclasses.field(
        default_factory=lambda: createBranchingTree(width=512, height=512)
    )

    def produce_smlm_frame(
        self,
        x_offset: int = 0,
        y_offset: int = 0,
        n_photons: int = 5000,
        n_photons_std: int = 50,
    ):
        """Generate a frame based on the current settings."""
        # add moise
        image = self.image.copy()
        # Adjust image based on offsets
        image = np.roll(np.roll(image, int(x_offset), axis=1), int(y_offset), axis=0)
        image = nip.extract(image, (self.sensor_width, self.sensor_height))

        yc_array, xc_array = self.binary2locs(image, density=self.density)
        photon_array = np.random.normal(n_photons, n_photons_std, size=len(xc_array))

        wavelenght = self.wave_length
        wavelenght_std = self.wave_length_std
        NA = self.NA
        sigma = 0.21 * wavelenght / NA  # change to get it from microscope settings
        sigma_std = (
            0.21 * wavelenght_std / NA
        )  # change to get it from microscope settings
        sigma_array = np.random.normal(sigma, sigma_std, size=len(xc_array))

        ADC_per_photon_conversion = (
            self.ADC_per_photon_conversion
        )  # change to get it from microscope settings
        readout_noise = self.readout_noise  # change to get it from microscope settings
        ADC_offset = self.ADC_offset  # change to get it from microscope settings

        out = FromLoc2Image_MultiThreaded(
            xc_array,
            yc_array,
            photon_array,
            sigma_array,
            self.sensor_height,
            self.pixel_size,
        )
        out = (
            ADC_per_photon_conversion * np.random.poisson(out)
            + readout_noise
            * np.random.normal(size=(self.sensor_height, self.sensor_width))
            + ADC_offset
        )
        return np.array(out)

    def binary2locs(self, img: np.ndarray, density: float):
        """
        Given a binary image `img` and a `density` value, this function returns a subset of the locations where the image is non-zero.
        Parameters:
            img (np.ndarray): A binary image.
            density (float): The density of the subset of locations to be returned.
        Returns:
            tuple: A tuple containing two numpy arrays representing the x and y coordinates of the subset of locations.
        """
        all_locs = np.nonzero(img == 1)
        n_points = int(len(all_locs[0]) * density)
        selected_idx = np.random.choice(len(all_locs[0]), n_points, replace=False)
        filtered_locs = all_locs[0][selected_idx], all_locs[1][selected_idx]
        return filtered_locs

    async def get_last(self) -> np.ndarray:

        return await asyncio.to_thread(
            self.produce_smlm_frame,
            x_offset=self.position.x,
            y_offset=self.position.y,
            n_photons=self.intensity,
            n_photons_std=self.intensity * self.intensity_std_dev,
        )

    async def compute_event(
        self, event: AcquireFrameEvent | ZChangeEvent
    ) -> AsyncGenerator[DataEvent, None]:

        if isinstance(event, AcquireFrameEvent):
            print("Acquiring frame")
            yield ImageDataEvent(data=await self.get_last())

        if isinstance(event, SetLightIntensityEvent):
            print("Setting light intensity")
            self.intensity = event.intensity

        if isinstance(event, AcquireTSeriesEvent):
            print("Acquiring Z-stack")
            for z in range(event.t_steps):
                yield ImageDataEvent(data=await self.get_last())

        if isinstance(event, AcquireZStackEvent):
            print("Acquiring Z-stack")
            z_stack = []
            for z in event.z_steps:
                self.position.z = z
                yield ImageDataEvent(data=await self.get_last())

        if isinstance(event, MoveEvent):
            print("Moving")
            if event.x:
                self.position.x = event.x
            if event.y:
                self.position.y = event.y
            if event.z:
                self.position.z = event.z

            yield HasMovedEvent(x=self.position.x, y=self.position.y, z=self.position.z)

    def challenge(self, event: ManagerEvent) -> bool:
        return isinstance(
            event,
            (
                AcquireFrameEvent,
                SetLightIntensityEvent,
                AcquireZStackEvent,
                MoveEvent,
                AcquireTSeriesEvent,
            ),
        )


@dataclasses.dataclass
class Camera:
    sensor_height: int = 512
    sensor_width: int = 512
    pixel_size: float = 1.0
    image: np.ndarray = dataclasses.field(
        default_factory=lambda: createBranchingTree(width=512, height=512)
    )

    def __post_init__(self):
        self.noise_stack = (
            np.random.randn(self.sensor_height, self.sensor_width, 100) * 2
        )

    def setPropertyValue(self, propertyName, propertyValue):
        pass


def createBranchingTree(width=5000, height=5000, lineWidth=3):
    np.random.seed(0)  # Set a random seed for reproducibility
    # Define the dimensions of the image
    width, height = 5000, 5000

    # Create a blank white image
    image = np.ones((height, width), dtype=np.uint8) * 255

    # Function to draw a line (blood vessel) on the image
    def draw_vessel(start, end, image):
        rr, cc = line(start[0], start[1], end[0], end[1])
        try:
            image[rr, cc] = 0  # Draw a black line
        except:
            end = 0
            return

    # Recursive function to draw a tree-like structure
    def draw_tree(start, angle, length, depth, image, reducer, max_angle=40):
        if depth == 0:
            return

        # Calculate the end point of the branch
        end = (
            int(start[0] + length * np.sin(np.radians(angle))),
            int(start[1] + length * np.cos(np.radians(angle))),
        )

        # Draw the branch
        draw_vessel(start, end, image)

        # change the angle slightly to add some randomness
        angle += np.random.uniform(-10, 10)

        # Recursively draw the next level of branches
        new_length = length * reducer  # Reduce the length for the next level
        new_depth = depth - 1
        draw_tree(
            end,
            angle - max_angle * np.random.uniform(-1, 1),
            new_length,
            new_depth,
            image,
            reducer,
        )
        draw_tree(
            end,
            angle + max_angle * np.random.uniform(-1, 1),
            new_length,
            new_depth,
            image,
            reducer,
        )

    # Starting point and parameters
    start_point = (height - 1, width // 2)
    initial_angle = -90  # Start by pointing upwards
    initial_length = np.max((width, height)) * 0.15  # Length of the first branch
    depth = 7  # Number of branching levels
    reducer = 0.9
    # Draw the tree structure
    draw_tree(start_point, initial_angle, initial_length, depth, image, reducer)

    # convolve image with rectangle
    rectangle = np.ones((lineWidth, lineWidth))
    image = convolve2d(image, rectangle, mode="same", boundary="fill", fillvalue=0)

    return image
