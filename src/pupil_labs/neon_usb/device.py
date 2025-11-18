from functools import cached_property

from pupil_labs.neon_usb.cameras.eye import EyeCamera
from pupil_labs.neon_usb.cameras.scene import SceneCamera


class Device:
    @cached_property
    def scene(self) -> SceneCamera:
        return SceneCamera()

    @cached_property
    def eye(self) -> EyeCamera:
        return EyeCamera()
