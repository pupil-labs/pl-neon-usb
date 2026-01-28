import cv2

from pupil_labs.neon_usb import EyeCameraUVC, SceneCamera

scene_cam = SceneCamera()
eye_cam = EyeCameraUVC()


while True:
    print("frame")
    scene_frame = scene_cam.get_frame()
    eye_frame = eye_cam.get_frame()

    cv2.imshow("Neon Eye Camera", eye_frame.gray)
    cv2.imshow("Neon Scene Camera", scene_frame.bgr)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break

cv2.destroyAllWindows()
