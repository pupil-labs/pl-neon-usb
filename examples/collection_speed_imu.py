import contextlib
import queue
import time
from threading import Event, Thread
from typing import TypeVar

from tqdm import tqdm

from pupil_labs.neon_usb import IMU, IMUData

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


def imu_receiver(
    output_q: queue.Queue[IMUData],
    start_event: Event,
    stop_event: Event,
    wait_event: Event | None = None,
) -> None:
    imu = IMU()
    start_event.set()
    if wait_event is not None:
        wait_event.wait()
    while True:
        if stop_event.is_set():
            break
        imu_data = imu.get_imu_data()
        with contextlib.suppress(queue.Full):
            output_q.put_nowait(imu_data)


imu_start_signal = Event()
imu_stop_signal = Event()
imu_q = queue.Queue[IMUData](maxsize=400)
imu_thread = Thread(
    target=imu_receiver,
    args=(imu_q, imu_start_signal, imu_stop_signal),
)
imu_thread.start()
imu_start_signal.wait()


total_frames = 500
frame_counter = 0
with tqdm(total=total_frames) as pbar:
    start = time.time()
    while True:
        if frame_counter >= total_frames:
            break

        imu_frames = get_all_items(imu_q)
        num_imu_frames = len(imu_frames)
        frame_counter += num_imu_frames

        pbar.update(num_imu_frames)

end = time.time()
imu_stop_signal.set()
print(f"IMU FPS: {frame_counter / (end - start):.1f} \t Duration: {end - start:.1f}")
