from pupil_labs.neon_usb import CameraNotFoundError, EyeCameraUVC, SceneCamera

scene_cam = SceneCamera()
eye_cam = EyeCameraUVC()

# Disconnect Neon while running this code to see the reconnection in action
while True:
    try:
        scene_frame = scene_cam.get_frame()
        eye_frame = eye_cam.get_frame()
    except TimeoutError:
        print(
            "\nTimeoutError - The device has been disconnected."
            " Attempting to reconnect.\n"
        )
        attempts = 0
        while True:
            try:
                # del eye_cam # When adding this line, the execution will freeze here
                scene_cam = SceneCamera()
                print("This gets printed.")
                eye_cam = EyeCameraUVC()
                print("This never gets printed.")
            except CameraNotFoundError:
                attempts += 1
                print("\033[1A", end="\x1b[2K")  # This line clears the previous line
                print(f"Device not yet reconnected. Retrying...{attempts}")
            else:
                print("Device reconnected.\n")
                break
        continue

    print(f"\rscene index: {scene_frame.index} \t eye index: {eye_frame.index}", end="")
