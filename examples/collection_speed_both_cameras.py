import queue
import time
from threading import Event, Thread

from tqdm import tqdm

from pupil_labs.neon_usb import (
    EyeCameraUVC,
    Frame,
    SceneCamera,
    get_all_items,
    image_receiver,
)

eye_start_event = Event()
eye_stop_event = Event()
scene_start_event = Event()
scene_stop_event = Event()

eye_q = queue.Queue[Frame](maxsize=400)
eye_thread = Thread(
    target=image_receiver,
    args=(EyeCameraUVC, eye_q, eye_start_event, eye_stop_event, scene_start_event),
)
eye_thread.start()


scene_q = queue.Queue[Frame](maxsize=400)
scene_thread = Thread(
    target=image_receiver,
    args=(SceneCamera, scene_q, scene_start_event, scene_stop_event, eye_start_event),
)
scene_thread.start()

eye_start_event.wait()
scene_start_event.wait()


total_eye_frames = 5000
eye_frame_counter = 0
scene_frame_counter = 0
with tqdm(total=total_eye_frames) as pbar:
    start = time.time()
    while True:
        if eye_frame_counter >= total_eye_frames:
            break
        eye_frames = get_all_items(eye_q)
        num_eye_frames = len(eye_frames)
        eye_frame_counter += num_eye_frames

        scene_frames = get_all_items(scene_q)
        num_scene_frames = len(scene_frames)
        scene_frame_counter += num_scene_frames

        pbar.update(num_eye_frames)

end = time.time()
eye_stop_event.set()
scene_stop_event.set()
print(
    "\t".join([
        f"Eye FPS: {eye_frame_counter / (end - start):.1f}",
        f"Scene FPS: {scene_frame_counter / (end - start):.1f}",
        f"Duration: {end - start:.1f}",
    ])
)
