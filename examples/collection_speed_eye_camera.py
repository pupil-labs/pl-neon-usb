import queue
import time
from threading import Event, Thread

from tqdm import tqdm

from pupil_labs.neon_usb import EyeCameraUVC, Frame, get_all_items, image_receiver

eye_start_signal = Event()
eye_stop_signal = Event()
eye_q = queue.Queue[Frame](maxsize=400)
eye_thread = Thread(
    target=image_receiver,
    args=(EyeCameraUVC, eye_q, eye_start_signal, eye_stop_signal),
)
eye_thread.start()
eye_start_signal.wait()


total_frames = 500
frame_counter = 0
with tqdm(total=total_frames) as pbar:
    start = time.time()
    while True:
        if frame_counter >= total_frames:
            break

        eye_frames = get_all_items(eye_q)
        num_eye_frames = len(eye_frames)
        frame_counter += num_eye_frames

        pbar.update(num_eye_frames)

end = time.time()
eye_stop_signal.set()
print(f"Eye FPS: {frame_counter / (end - start):.1f} \t Duration: {end - start:.1f}")

# eye_cam = EyeCam()
# num_frames = 5000
# start = time.time()
# for i in tqdm(range(num_frames)):
#     eye_frame = eye_cam.get_frame()
# end = time.time()
# print(f"FPS: {num_frames / (end - start):.1f}")
