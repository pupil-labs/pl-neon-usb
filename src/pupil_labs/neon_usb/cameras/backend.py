import time
from abc import ABC, abstractmethod
from pathlib import Path

import cv2
import numpy as np
import uvc
from pyrav4l2 import Device, v4l2

from ..frame import Frame
from ..v4lstream import V4lStream
from .camera import CameraNotFoundError, CameraSpec


class CameraBackend(ABC):
    def __init__(self, spec: CameraSpec):
        self.spec = spec

    @abstractmethod
    def get_frame(self) -> Frame:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def set_eye_exposure(self, eyeID, value) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.close()


class UVCBackend(CameraBackend):
    def __init__(self, spec: CameraSpec, extended_controls=None):
        super().__init__(spec)

        self._uvc_capture = None
        self.spec = spec
        self.extended_controls = extended_controls
        self.exposure_controls = None

        connected_devices = uvc.device_list()
        uid = None
        for device_info in connected_devices:
            if device_info["name"] == self.spec.name:
                uid = device_info["uid"]
                break

        if uid is None:
            raise CameraNotFoundError(self.spec.name)

        capture = uvc.Capture(uid, self.extended_controls)
        capture.bandwidth_factor = self.spec.bandwidth_factor

        mode_matched = False
        for mode in capture.available_modes:
            if (mode.width, mode.height, mode.fps) == (
                self.spec.width,
                self.spec.height,
                self.spec.fps,
            ):
                mode_matched = True
                capture.frame_mode = mode
                self.last_frame_timestamp: float = uvc.get_time_monotonic()
                self._uvc_capture = capture

                break

        if not mode_matched:
            capture.close()
            raise OSError(
                f"None of the available modes matched: {capture.available_modes}!"
            )

    def get_frame(self) -> Frame:
        if self._uvc_capture is None:
            raise OSError("Camera not initialized!")

        frame = self._uvc_capture.get_frame(timeout=2.0)
        frame.timestamp = self.last_frame_timestamp = uvc.get_time_monotonic()
        assert frame is not None
        return frame

    def close(self) -> None:
        if self._uvc_capture is not None:
            self._uvc_capture.close()
            del self._uvc_capture
        self._uvc_capture = None

    def set_eye_exposure(self, side_idx, exposure_time) -> None:
        if self.exposure_controls is None:
            uvc_controls = {c.display_name: c for c in self._uvc_capture.controls}
            self.exposure_controls = (
                uvc_controls["Primary Sensor Exposure"],
                uvc_controls["Secondary Sensor Exposure"],
            )

        self.exposure_controls[side_idx].value = int(exposure_time)


class V4l2Backend(CameraBackend):
    def __init__(self, spec: CameraSpec):
        super().__init__(spec)

        self.camera_reinit_timeout = 3
        self.device = None
        self.frame_counter = -1

        for device_path in Path("/dev/").glob("video*"):
            try:
                device = Device(device_path)
            except AttributeError:
                continue
            except FileNotFoundError:
                continue
            except PermissionError:
                continue

            if self.spec.name in device.device_name and device.is_video_capture_capable:
                formats = []
                for color_format, frame_sizes in device.available_formats.items():
                    for frame_size in frame_sizes:
                        for frame_interval in device.get_available_frame_intervals(
                            color_format, frame_size
                        ):
                            formats.append((color_format, frame_size, frame_interval))

                for color_format, frame_size, frame_interval in formats:
                    fps = frame_interval.denominator / frame_interval.numerator
                    if (frame_size.width, frame_size.height, fps) == (
                        self.spec.width,
                        self.spec.height,
                        self.spec.fps,
                    ):
                        device.set_format(color_format, frame_size)
                        device.set_frame_interval(frame_interval)
                        self.device = device
                        self.stream = V4lStream(self.device)
                        self.stream.open()
                        self._fd = open(self.device.path)
                        self.color_format, _ = self.device.get_format()

                        break

                else:
                    raise OSError("None of the available modes matched!")

        if self.device is None:
            raise CameraNotFoundError(self.spec.name)

    def get_frame(self) -> Frame:
        buffer = self.stream.get_frame()
        if buffer is None:
            raise TimeoutError

        if self.color_format.pixelformat == v4l2.V4L2_PIX_FMT_GREY:
            pixels = np.frombuffer(buffer, dtype=np.uint8).reshape([
                self.spec.height,
                self.spec.width,
            ])
        elif self.color_format.pixelformat == v4l2.V4L2_PIX_FMT_MJPEG:
            pixels = cv2.imdecode(np.frombuffer(buffer, np.uint8), cv2.IMREAD_COLOR)

        self.frame_counter += 1

        return Frame(pixels, time.time(), self.frame_counter)

    def close(self) -> None:
        self._fd.close()

    def set_eye_exposure(self, side_idx, exposure_time) -> None:
        self.exposure_controls[side_idx].value = int(exposure_time)
