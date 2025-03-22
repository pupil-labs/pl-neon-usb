from typing import Tuple

from pupil_labs.gazenet.usb_utils import get_intrinsics_data

from .backend import UVCBackend
from .camera import Camera, CameraSpec

CameraMatrix = Tuple[
    Tuple[float, float, float],
    Tuple[float, float, float],
    Tuple[float, float, float],
]

DistortionCoeffs = Tuple[float, ...]
CameraIntrinsics = Tuple[CameraMatrix, DistortionCoeffs]


class SceneCam(Camera):
    """The `SceneCam` class provides an interface for handling the Neon scene
    camera.

    The class is assuming that no more than one Neon device is connected to the
    computer at the same time.
    """

    def __init__(self):
        """Initializes the scene camera of the connected Neon device.

        The camera stream will be started right away. If the object fails to grab
        frames, it will automatically try to reinitialize.
        """
        spec = CameraSpec(
            name="Neon Scene Camera v1",
            vendor_id=0x0BDA,
            product_id=0x3036,
            width=1600,
            height=1200,
            fps=30,
            bandwidth_factor=1.2,
        )
        super().__init__(spec, UVCBackend)

        self.uvc_controls = {
            c.display_name: c for c in self.backend._uvc_capture.controls
        }
        camera_parameters = {
            "Backlight Compensation": 2,
            "Brightness": 0,
            "Contrast": 32,
            "Gain": 64,
            "Hue": 0,
            "Saturation": 64,
            "Sharpness": 50,
            "Gamma": 300,
            "Auto Exposure Mode": 1,
            "Absolute Exposure Time": 250,
        }
        for key, value in camera_parameters.items():
            try:
                self.uvc_controls[key].value = value
            except KeyError:
                print(f"Setting {key} to {value} failed: Unknown control. Known ")

    @staticmethod
    def get_intrinsics() -> CameraIntrinsics:
        """Retrieves the scene camera intrinsics of the Neon device including
        the camera matrix and distortion coefficients.

        Returns:
            A tuple containing the camera matrix and distortion coefficients of the scene camera.

        """
        return get_intrinsics_data()
