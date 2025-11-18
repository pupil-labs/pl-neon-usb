import queue
from threading import Event
from typing import TypeVar

from pupil_labs.neon_usb import EyeCamera, Frame, SceneCamera

T = TypeVar("T")


def get_all_items(q: queue.Queue[T]) -> list[T]:
    """Retrieve all items from a queue and always at least one."""
    items = []
    # Need to get at least one item
    # Otherwise the queue might be spammed with requests
    items.append(q.get())
    while True:
        try:
            items.append(q.get_nowait())
        except queue.Empty:
            break
    return items


def image_receiver(
    CameraClass: type[SceneCamera | EyeCamera],
    output_q: queue.Queue[Frame],
    start_event: Event,
    stop_event: Event,
    wait_event: Event | None = None,
) -> None:
    cam = CameraClass()
    start_event.set()
    if wait_event is not None:
        wait_event.wait()
    while True:
        if stop_event.is_set():
            cam.close()
            break
        eye_img = cam.get_frame()
        output_q.put_nowait(eye_img)
