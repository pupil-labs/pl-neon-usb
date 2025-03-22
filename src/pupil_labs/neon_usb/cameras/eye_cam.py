import cv2
import numpy as np

from ..uvc_utils import set_eye_exposure
from .backend import V4l2Backend
from .camera import Camera, CameraSpec, Frame


class Exposure_Time:
    def __init__(self, max_ET, frame_rate, mode="manual"):
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
        self.last_check_timestamp = None

    def calculate_based_on_frame(self, frame):
        if self.last_check_timestamp is None:
            self.last_check_timestamp = frame.timestamp

        if frame.timestamp - self.last_check_timestamp > self.check_freq:
            if self.mode == "manual":
                self.last_ETs = [self.ET_thres[1]] * 2
                return [self.ET_thres[1]] * 2

            elif self.mode == "auto":
                half_width = frame.gray.shape[1] // 2

                next_ETs = []
                for side_idx in (0, 1):
                    image_half = frame.gray[
                        :, side_idx * half_width : (side_idx + 1) * half_width
                    ]
                    image_block = cv2.resize(image_half, dsize=self.AE_Win.shape)
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


class EyeCam(Camera):
    """The `EyeCam` class provides an interface for handling the Neon eye
    cameras.

    The class is assuming that no more than one Neon device is connected to the
    computer at the same time.

    Note that the two eye cameras is Neon are treated as a single device.
    Grabbing a frame from the `EyeCam` class will return a single frame
    containing images from both cameras.
    """

    def __init__(self):
        """Initializes the eye cameras of the connected Neon device.

        The camera stream will be started right away. If the object fails to grab
        frames, it will automatically try to reinitialize.
        """
        print("Yeay!")
        spec = CameraSpec(
            name="Neon Sensor Module v1",
            vendor_id=0x16D0,
            product_id=0x11D3,
            width=384,
            height=192,
            fps=200,
            bandwidth_factor=0,
        )
        super().__init__(spec, V4l2Backend)
        self.exposure_algorithm = Exposure_Time(max_ET=28, frame_rate=200, mode="auto")

    def get_frame(self) -> Frame:
        frame = super().get_frame()

        if self.exposure_algorithm is not None:
            exposure_times = self.exposure_algorithm.calculate_based_on_frame(frame)
            if exposure_times is not None:
                for side_idx, exposure_time in enumerate(exposure_times):
                    set_eye_exposure(self.backend._fd, side_idx, exposure_time)

        return frame
