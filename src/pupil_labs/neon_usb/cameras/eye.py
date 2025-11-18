from typing import Literal

import cv2
import numpy as np

from pupil_labs.neon_usb.usb_utils import USB_ID_PRODUCT, USB_ID_VENDOR

from ..uvc_utils import get_eye_exposure, set_eye_exposure
from .backend import V4l2Backend
from .camera import Camera, CameraSpec, Frame

ExposureMode = Literal["manual", "auto"]


NEON_EYE_CAMERA_SPEC = CameraSpec(
    name="Neon Sensor Module v1",
    vendor_id=USB_ID_VENDOR,
    product_id=USB_ID_PRODUCT,
    width=384,
    height=192,
    fps=200,
    bandwidth_factor=0,
)


class Exposure_Time:
    def __init__(
        self, max_ET: float, frame_rate: float, mode: ExposureMode = "manual"
    ) -> None:
        self.mode = mode
        self.ET_thres = 1, min(10000 / frame_rate, max_ET)
        self.last_ETs = [self.ET_thres[1]] * 2

        self.targetY_thres = 90, 150

        self.AE_Win = np.array([
            [3, 1, 1, 1, 1, 1, 1, 3],
            [3, 1, 1, 1, 1, 1, 1, 3],
            [2, 1, 1, 1, 1, 1, 1, 2],
            [2, 1, 1, 1, 1, 1, 1, 2],
            [2, 1, 1, 1, 1, 1, 1, 2],
            [2, 1, 1, 1, 1, 1, 1, 2],
            [3, 1, 1, 1, 1, 1, 1, 3],
            [3, 1, 1, 1, 1, 1, 1, 3],
        ])
        self.smooth = 1 / 3
        self.check_freq = 0.1 / 3
        self.last_check_timestamp: float | None = None

    def calculate_based_on_frame(
        self, timestamp: float, image: np.ndarray
    ) -> list[float] | None:
        if self.last_check_timestamp is None:
            self.last_check_timestamp = timestamp

        if timestamp - self.last_check_timestamp > self.check_freq:
            if self.mode == "manual":
                self.last_ETs = [self.ET_thres[1]] * 2
                return [self.ET_thres[1]] * 2

            elif self.mode == "auto":
                half_width = len(image[1]) // 2

                next_ETs = []
                for side_idx in (0, 1):
                    image_half = image[
                        :, side_idx * half_width : (side_idx + 1) * half_width
                    ]
                    dsize = self.AE_Win.shape[0], self.AE_Win.shape[1]
                    image_block = cv2.resize(image_half, dsize=dsize)
                    YTotal = max(
                        np.multiply(self.AE_Win, image_block).sum() / self.AE_Win.sum(),
                        1,
                    )

                    last_ET = self.last_ETs[side_idx]

                    if YTotal < self.targetY_thres[0]:
                        targetET = last_ET * self.targetY_thres[0] / YTotal
                    elif YTotal > self.targetY_thres[1]:
                        targetET = last_ET * self.targetY_thres[1] / YTotal
                    else:
                        targetET = last_ET

                    next_ET = np.clip(
                        last_ET + (targetET - last_ET) * self.smooth,
                        self.ET_thres[0],
                        self.ET_thres[1],
                    )
                    self.last_ETs[side_idx] = next_ET
                    next_ETs.append(next_ET)

                return next_ETs
        return None


class EyeCamera(Camera):
    """Provides an interface for handling the Neon eye cameras.

    The class is assuming that no more than one Neon device is connected to the
    computer at the same time.

    Note that the two eye cameras is Neon are treated as a single device.
    Grabbing a frame from the `EyeCam` class will return a single frame
    containing images from both cameras.
    """

    def __init__(self, spec: CameraSpec = NEON_EYE_CAMERA_SPEC) -> None:
        """Initialize the eye cameras of the connected Neon device.

        The camera stream will be started right away. If the object fails to grab
        frames, it will automatically try to reinitialize.
        """
        super().__init__(spec, V4l2Backend)
        self.exposure_algorithm: Exposure_Time | None = Exposure_Time(
            max_ET=28, frame_rate=200, mode="auto"
        )

    def get_frame(self) -> Frame:
        frame = super().get_frame()

        if self.exposure_algorithm is not None:
            exposure_times = self.exposure_algorithm.calculate_based_on_frame(
                frame.timestamp, frame.gray
            )

            if exposure_times is not None:
                for side_idx, exposure_time in enumerate(exposure_times):
                    self._set_eye_exposure(side_idx, int(exposure_time))

        return frame

    @property
    def exposure(self) -> tuple[int | None, int | None]:
        return (self._get_eye_exposure(0), self._get_eye_exposure(1))

    @exposure.setter
    def exposure(self, exposure_time: int | tuple[int, int]) -> None:
        values = (
            exposure_time
            if isinstance(exposure_time, tuple)
            else [exposure_time, exposure_time]
        )
        for eye_idx, value in enumerate(values):
            self._set_eye_exposure(eye_idx, value)

    def _get_eye_exposure(self, eye_idx: int) -> int | None:
        assert isinstance(self.backend, V4l2Backend)
        return get_eye_exposure(self.backend._fd, eye_idx)

    def _set_eye_exposure(self, eye_idx: int, exposure_time: int) -> None:
        assert isinstance(self.backend, V4l2Backend)
        self.exposure_algorithm = None
        set_eye_exposure(self.backend._fd, eye_idx, exposure_time)
