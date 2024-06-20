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
    AcquireTSeriesEvent,
    AcquireZStackEvent,
    DataEvent,
    ImageDataEvent,
    ManagerEvent,
    MoveEvent,
    SetLightIntensityEvent,
    ZChangeEvent,
)
from akuire.managers.base import Manager

IS_NIP = True


FILE_PATH = get_absolute_path("big.jpg")


class VirtualMicroscopeManager(Manager):

    def __init__(self, filePath=FILE_PATH):
        self.camera = Camera(self, filePath)
        self.positioner = Positioner(self)
        self.illuminator = Illuminator(self)

    async def compute_event(
        self, event: AcquireFrameEvent | ZChangeEvent
    ) -> AsyncGenerator[DataEvent, None]:

        if isinstance(event, AcquireFrameEvent):
            print("Acquiring frame")
            yield ImageDataEvent(data=self.camera.getLast())

        if isinstance(event, SetLightIntensityEvent):
            print("Setting light intensity")
            self.illuminator.set_intensity(event.intensity)

        if isinstance(event, AcquireZStackEvent):
            print("Acquiring Z-stack")
            z_stack = []
            for z in event.z_values:
                self.positioner.move(z=z)
                z_stack.append(self.camera.getLast())
            yield ImageDataEvent(data=z_stack)

        if isinstance(event, MoveEvent):
            print("Moving")
            self.positioner.move(x=event.x, y=event.y, z=event.z)

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


class Camera:
    def __init__(self, parent, filePath="simplant"):
        self._parent = parent
        if filePath == "simplant":
            self.image = createBranchingTree(width=5000, height=5000)
        else:
            self.image = np.mean(cv2.imread(filePath), axis=2)

        self.image /= np.max(self.image)
        self.SensorWidth = 512  # self.image.shape[1]
        self.SensorHeight = 512  # self.image.shape[0]
        self.model = "VirtualCamera"
        self.PixelSize = 1.0
        self.isRGB = False
        self.frameNumber = 0
        # precompute noise so that we will save energy and trees
        self.noiseStack = np.random.randn(self.SensorHeight, self.SensorWidth, 100) * 2

    def produce_frame(
        self, x_offset=0, y_offset=0, light_intensity=1.0, defocusPSF=None
    ):
        """Generate a frame based on the current settings."""
        # add moise
        image = self.image.copy()
        # Adjust image based on offsets
        image = np.roll(np.roll(image, int(x_offset), axis=1), int(y_offset), axis=0)
        image = nip.extract(image, (self.SensorWidth, self.SensorHeight))

        # do all post-processing on cropped image
        if IS_NIP and defocusPSF is not None and not defocusPSF.shape == ():
            print("Defocus:" + str(defocusPSF.shape))
            image = np.array(np.real(nip.convolve(image, defocusPSF)))
        image = np.float32(image) / np.max(image) * np.float32(light_intensity)
        image += self.noiseStack[:, :, np.random.randint(0, 100)]

        # Adjust illumination
        image = image.astype(np.uint16)
        print(image.shape)
        reshaped = np.array(image).reshape(
            (1, 1, 1, self.SensorHeight, self.SensorWidth)
        )
        print(reshaped.shape)
        return reshaped

    def getLast(self, returnFrameNumber=False):
        position = self._parent.positioner.get_position()
        defocusPSF = np.squeeze(self._parent.positioner.get_psf())
        intensity = self._parent.illuminator.get_intensity(1)
        self.frameNumber += 1
        if returnFrameNumber:
            return (
                self.produce_frame(
                    x_offset=position["X"],
                    y_offset=position["Y"],
                    light_intensity=intensity,
                    defocusPSF=defocusPSF,
                ),
                self.frameNumber,
            )
        else:
            return self.produce_frame(
                x_offset=position["X"],
                y_offset=position["Y"],
                light_intensity=intensity,
                defocusPSF=defocusPSF,
            )

    def setPropertyValue(self, propertyName, propertyValue):
        pass


class Positioner:
    def __init__(self, parent):
        self._parent = parent
        self.position = {"X": 0, "Y": 0, "Z": 0, "A": 0}
        self.mDimensions = (
            self._parent.camera.SensorWidth,
            self._parent.camera.SensorHeight,
        )
        if IS_NIP:
            self.psf = self.compute_psf(dz=0)
        else:
            self.psf = None

    def move(self, x=None, y=None, z=None, a=None, is_absolute=True):
        if is_absolute:
            if x is not None:
                self.position["X"] = x
            if y is not None:
                self.position["Y"] = y
            if z is not None:
                self.position["Z"] = z
                self.compute_psf(self.position["Z"])
            if a is not None:
                self.position["A"] = a
        else:
            if x is not None:
                self.position["X"] += x
            if y is not None:
                self.position["Y"] += y
            if z is not None:
                self.position["Z"] += z
                self.compute_psf(self.position["Z"])
            if a is not None:
                self.position["A"] += a

    def get_position(self):
        return self.position.copy()

    def compute_psf(self, dz):
        dz = np.float32(dz)
        print("Defocus:" + str(dz))
        if IS_NIP and dz != 0:
            obj = nip.image(np.zeros(self.mDimensions))
            obj.pixelsize = (100.0, 100.0)
            paraAbber = nip.PSF_PARAMS()
            # aber_map = nip.xx(obj.shape[-2:]).normalize(1)
            paraAbber.aberration_types = [paraAbber.aberration_zernikes.spheric]
            paraAbber.aberration_strength = [np.float32(dz) / 10]
            psf = nip.psf(obj, paraAbber)
            self.psf = psf.copy()
            del psf
            del obj
        else:
            self.psf = None

    def get_psf(self):
        return self.psf


class Illuminator:
    def __init__(self, parent):
        self._parent = parent
        self.intensity = 100

    def set_intensity(self, intensity=0):
        self.intensity = intensity

    def get_intensity(self, channel):
        return self.intensity


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
