from types import TracebackType
from typing import TYPE_CHECKING, NamedTuple

from pupil_labs.neon_usb.frame import Frame

if TYPE_CHECKING:
    from pupil_labs.neon_usb.cameras.backend import CameraBackend


class CameraSpec(NamedTuple):
    name: str
    vendor_id: int
    product_id: int
    width: int
    height: int
    fps: int
    bandwidth_factor: float


class CameraNotFoundError(Exception):
    def __init__(self, name: str) -> None:
        self.camera_name = name
        super().__init__(f"Camera '{name}' not found!")


class Camera:
    def __init__(self, spec: CameraSpec, backend_class: type["CameraBackend"]) -> None:
        self.backend = backend_class(spec)
        self.spec = spec
        self.frame_counter = -1

    def get_frame(self) -> Frame:
        return self.backend.get_frame()

    def close(self) -> None:
        self.backend.close()

    def __enter__(self) -> "Camera":
        return self

    def __exit__(
        self,
        type_: type[BaseException] | None,
        value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return self.close()
